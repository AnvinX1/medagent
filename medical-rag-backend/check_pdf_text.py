from langchain_community.document_loaders import PyPDFLoader
import glob
import os

DATA_PATH = "data"

def check_text():
    files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    if not files:
        print("No PDFs found.")
        return

    for f in files:
        print(f"--- Checking {f} ---")
        try:
            loader = PyPDFLoader(f)
            pages = loader.load()
            if not pages:
                print("No pages extracted.")
                continue
            
            print(f"Loaded {len(pages)} pages.")
            print("--- Page 1 Content ---")
            print(pages[0].page_content[:500])
            print("\n--- Page 10 Content (if exists) ---")
            if len(pages) > 10:
                print(pages[10].page_content[:500])
        except Exception as e:
            print(f"Error loading {f}: {e}")

if __name__ == "__main__":
    check_text()
