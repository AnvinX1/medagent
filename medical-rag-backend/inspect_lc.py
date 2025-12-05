import langchain
import os
import sys

print(f"langchain version: {langchain.__version__}")
print(f"langchain path: {langchain.__file__}")
print(f"langchain dir: {dir(langchain)}")

try:
    import langchain.chains
    print("langchain.chains imported")
except ImportError as e:
    print(f"ImportError chains: {e}")

try:
    from langchain_community.chains import RetrievalQA
    print("Imported RetrievalQA from langchain_community.chains")
except ImportError:
    print("Could not import RetrievalQA from langchain_community.chains")

# List files in langchain directory
lc_dir = os.path.dirname(langchain.__file__)
print(f"Listing {lc_dir}:")
try:
    print(os.listdir(lc_dir))
except Exception as e:
    print(f"Error listing dir: {e}")
