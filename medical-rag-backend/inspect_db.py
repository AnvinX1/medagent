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
        print("Vector store initialized.")
        
        # Get all documents (limit to 5 to avoid spam)
        results = vector_store.get(limit=5)
        
        if not results['ids']:
            print("Database appears empty (no IDs found).")
        else:
            print(f"Found {len(results['ids'])} documents (showing first 5).")
            for i, meta in enumerate(results['metadatas']):
                print(f"Doc {i}: Source = {meta.get('source')}")

        # Test Query
        print("\n--- Testing Search for 'Polycystic' ---")
        query = "Polycystic"
        results = vector_store.similarity_search(query, k=5)
        if not results:
             print("Search returned NO results.")
        for i, doc in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Source: {doc.metadata.get('source')}")
            print(f"Content: {doc.page_content[:200].replace(chr(10), ' ')}...") # Show snippet
            
    except Exception as e:
        print(f"Error acting on database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_db()
