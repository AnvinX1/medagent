# Medical AI Backend

This is a local-first, privacy-centric RAG architecture using FastAPI, ChromaDB, and Ollama.

## Setup

1.  **Install Dependencies**:
    The project is initialized with `uv`. Dependencies are already added.

2.  **Add Data**:
    Place your medical PDF files in the `data/` directory.

3.  **Ingest Data**:
    Run the ingestion script to process PDFs and store them in ChromaDB.
    ```bash
    uv run ingest.py
    ```

4.  **Run the API**:
    Start the FastAPI server.
    ```bash
    uv run app/main.py
    ```
    Or using uvicorn directly:
    ```bash
    uv run uvicorn app.main:app --reload
    ```

## API Usage

-   **Endpoint**: `POST /chat`
-   **Body**: `{"query": "Your medical question here"}`
-   **Response**: JSON containing the answer and source documents.

## Configuration

-   **Model**: Default is `llama3`. You can change it by setting the `MODEL_NAME` environment variable.
-   **Embeddings**: Uses `nomic-embed-text` via Ollama. Ensure you have pulled these models in Ollama:
    ```bash
    ollama pull llama3
    ollama pull nomic-embed-text
    ```
