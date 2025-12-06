from langchain_community.document_loaders import PDFPlumberLoader
import glob
import os

DATA_PATH = "data"

def grep_text(term):
    files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    for f in files:
        print(f"--- Scanning {f} for '{term}' ---")
        try:
            loader = PDFPlumberLoader(f)
            pages = loader.load()
            found = False
            for i, p in enumerate(pages):
                if term.lower() in p.page_content.lower():
                    print(f"Found '{term}' on page {i+1}")
                    print(f"Content snippet: {p.page_content[:200].replace(chr(10), ' ')}...")
                    found = True
                    # Don't break, find all occurrences to see if it's just in the TOC
        
            if not found:
                print(f"'{term}' NOT FOUND in {f}")
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    grep_text("PCOS")
    grep_text("Polycystic")
