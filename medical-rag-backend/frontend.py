import streamlit as st
import requests
import os
import shutil
import uuid

# Configuration
API_URL = "http://localhost:8000/chat"
DOCS_URL = "http://localhost:8000/documents"
DATA_DIR = "data"

st.set_page_config(page_title="Medical AI Companion", layout="wide")

st.title("Medical AI Companion")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar
with st.sidebar:
    st.header("Knowledge Base")
    
    # File Upload
    uploaded_files = st.file_uploader("Upload Medical PDFs", type="pdf", accept_multiple_files=True)
    if st.button("Process Documents"):
        if uploaded_files:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            
            saved_count = 0
            for uploaded_file in uploaded_files:
                file_path = os.path.join(DATA_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_count += 1
            
            st.success(f"Saved {saved_count} files.")
            
            with st.spinner("Ingesting documents..."):
                try:
                    from ingest import ingest_documents
                    ingest_documents()
                    st.success("Ingestion complete!")
                    st.rerun() # Refresh to show new files in list
                except Exception as e:
                    st.error(f"Ingestion failed: {str(e)}")
        else:
            st.warning("Please upload files first.")

    st.divider()
    
    # Source Selection
    st.subheader("Active Knowledge Base")
    try:
        response = requests.get(DOCS_URL)
        if response.status_code == 200:
            available_docs = response.json().get("documents", [])
        else:
            available_docs = []
            st.error("Could not fetch document list.")
    except:
        available_docs = []
        st.warning("Backend not reachable.")

    selected_docs = st.multiselect(
        "Select documents to search:",
        options=available_docs,
        default=available_docs,
        help="The agent will only search within these selected files."
    )

# Chat Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a medical question or request an action..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt, 
                    "session_id": st.session_state.session_id,
                    "doc_filters": selected_docs if selected_docs else None
                }
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided.")
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"Connection failed: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
