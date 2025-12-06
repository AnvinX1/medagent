import os
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

DB_PATH = "db" # Assuming running from root

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Inspecting database at {DB_PATH}...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    try:
        vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        # Get all documents (limit to 5 to avoid spam)
        results = vector_store.get(limit=5)
        
        if not results['ids']:
            print("Database is empty.")
            return

        print(f"Found {len(results['ids'])} documents (showing first 5).")
        for i, meta in enumerate(results['metadatas']):
            print(f"Doc {i}: Source = {meta.get('source')}")
            
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    inspect_db()
