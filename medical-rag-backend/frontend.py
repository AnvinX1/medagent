import streamlit as st
import requests
import os
import shutil
import uuid
import pandas as pd

# Configuration
API_URL = "http://localhost:8000"
CHAT_URL = f"{API_URL}/chat"
DOCS_URL = f"{API_URL}/documents"
HEALTH_URL = f"{API_URL}/health-metrics"
APPT_URL = f"{API_URL}/appointments"
USAGE_URL = f"{API_URL}/usage-stats"
DATA_DIR = "data"

st.set_page_config(page_title="Medical AI Companion", layout="wide")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- Page Functions ---

def render_chat_page():
    st.title("Medical AI Companion")
    
    # Sidebar for Chat Page
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
                        st.rerun() 
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
                    response = requests.post(CHAT_URL, json=payload)
                    
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

def render_health_tracker():
    st.title("Daily Health Tracker")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Entry")
        with st.form("health_form"):
            metric_type = st.selectbox("Metric", ["Heart Rate", "Blood Pressure", "Weight", "Blood Sugar", "Temperature"])
            value = st.number_input("Value", min_value=0.0, step=0.1)
            unit = st.text_input("Unit", value="bpm" if metric_type == "Heart Rate" else "kg")
            
            submitted = st.form_submit_button("Save Entry")
            if submitted:
                try:
                    payload = {"metric_type": metric_type, "value": value, "unit": unit}
                    res = requests.post(HEALTH_URL, json=payload)
                    if res.status_code == 200:
                        st.success("Saved!")
                        st.rerun()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    with col2:
        st.subheader("History")
        try:
            res = requests.get(HEALTH_URL)
            if res.status_code == 200:
                data = res.json().get("metrics", [])
                if data:
                    df = pd.DataFrame(data)
                    df["date"] = pd.to_datetime(df["date"])
                    
                    # Filter by metric for chart
                    selected_metric = st.selectbox("Select Metric to Visualize", df["metric"].unique())
                    metric_df = df[df["metric"] == selected_metric]
                    
                    st.line_chart(metric_df, x="date", y="value")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No health data recorded yet.")
            else:
                st.error("Failed to fetch data.")
        except Exception as e:
            st.error(f"Connection failed: {e}")

def render_appointments():
    st.title("Appointments")
    st.info("You can schedule appointments by asking the Chat Agent (e.g., 'Schedule appointment for John at 5pm').")
    
    try:
        res = requests.get(APPT_URL)
        if res.status_code == 200:
            data = res.json().get("appointments", [])
            if data:
                df = pd.DataFrame(data)
                st.table(df)
            else:
                st.info("No upcoming appointments.")
        else:
            st.error("Failed to fetch appointments.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

def render_usage_stats():
    st.title("Usage Dashboard")
    
    try:
        res = requests.get(USAGE_URL)
        if res.status_code == 200:
            data = res.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Messages", data.get("total_messages", 0))
            with col2:
                st.metric("Unique Sessions", data.get("unique_sessions", 0))
                
            st.markdown("### Detailed Stats")
            st.write("More detailed analytics coming soon in Pro version.")
        else:
            st.error("Failed to fetch stats.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

def render_pro_page():
    st.title("Pro Features")
    
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
        <h2>Upgrade to Medical AI Pro</h2>
        <ul>
            <li>Unlimited Document Uploads</li>
            <li>Advanced Analytics & Trends</li>
            <li>Multi-User Support</li>
            <li>Priority Support</li>
        </ul>
        <button style="background-color: #ff4b4b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
            Upgrade Now ($9.99/mo)
        </button>
    </div>
    """, unsafe_allow_html=True)

# --- Main Navigation ---

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Health Tracker", "Appointments", "Usage Dashboard", "Pro Version"])

if page == "Chat":
    render_chat_page()
elif page == "Health Tracker":
    render_health_tracker()
elif page == "Appointments":
    render_appointments()
elif page == "Usage Dashboard":
    render_usage_stats()
elif page == "Pro Version":
    render_pro_page()
