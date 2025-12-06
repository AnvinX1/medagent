import os
import logging
import warnings
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Suppress warnings
logging.getLogger("pypdf").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "db")

def ingest_documents(status_callback=None, clear_db=True):
    # Clear existing database
    if clear_db and os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"Cleared existing database at {DB_PATH}")

    # 1. Load Documents
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created {DATA_PATH} directory. Please put PDF files there.")
        return

    print(f"Loading documents from {DATA_PATH}...")
    
    documents = []
    pdf_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in data/ directory.")
        if status_callback:
            status_callback("No PDF documents found.")
        return

    for pdf_file in pdf_files:
        file_path = os.path.join(DATA_PATH, pdf_file)
        if status_callback:
            msg = f"Loading {pdf_file}..."
            try:
                # status_callback expects (processed, total) usually, but we overloaded it in previous edits
                # Let's check frontend.py usage. 
                # Frontent usage: ingest_documents(status_callback=update_progress)
                # update_progress(current, total) OR update_progress(msg) logic?
                # In frontend.py: 
                # def update_progress(current, total):
                #     progress_bar.progress(current / total, text=f"Processed {current}/{total} chunks")
                # So it expects (int, int).
                # But my previous edit passed strings? No, I must have been careful.
                # Wair, I need to check frontend.py again to be sure I don't break the callback.
                pass
            except:
                pass

        try:
            loader = PDFPlumberLoader(file_path)
            docs = loader.load()
            # Ensure metadata source is set correctly
            for doc in docs:
                doc.metadata["source"] = file_path
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")

    print(f"Loaded {len(documents)} document pages.")

    if not documents:
        return

    # 2. Split Documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    # 3. Embed and Store
    embedding_model = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text")
    print(f"Initializing embeddings ({embedding_model})...")
    embeddings = OllamaEmbeddings(model=embedding_model)
    
    # Initialize Chroma
    print(f"Creating vector store in {DB_PATH}...")
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )
    
    batch_size = 50
    total_chunks = len(chunks)
    print(f"Processing {total_chunks} chunks in batches of {batch_size}...")
    
    for i in range(0, total_chunks, batch_size):
        batch = chunks[i:i + batch_size]
        try:
            vector_store.add_documents(batch)
            current = min(i + batch_size, total_chunks)
            print(f"Processed {current}/{total_chunks} chunks...")
            if status_callback:
                status_callback(current, total_chunks)
        except Exception as e:
            print(f"Error adding batch {i} to vector store: {e}")
    
    print(f"Saved {len(chunks)} chunks to {DB_PATH}.")

if __name__ == "__main__":
    ingest_documents()
