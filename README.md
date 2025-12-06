# Hygeia AI - Medical RAG Application

A comprehensive medical AI assistant combining a **FastAPI** backend with a **Next.js** frontend. Features include Retrieval-Augmented Generation (RAG) on medical PDFs, health metric tracking, and appointment scheduling.

## 🚀 Prerequisites

1.  **Python 3.10+** (Recommend using `uv` for package management)
2.  **Node.js 18+** (and `npm`)
3.  **Ollama** running locally with the following models:
    ```bash
    ollama pull qwen3-coder:latest
    ollama pull nomic-embed-text
    ```

## 🛠️ Installation & Setup

### 1. Backend Setup

Navigate to the backend directory:
```bash
cd medical-rag-backend
```

Create a `.env` file (if not exists) with your configuration:
```ini
# .env
DATABASE_URL=postgresql://neondb_owner:npg_e5ykHrGpqxs0@ep-frosty-tree-afvvp26t-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require
MODEL_NAME=qwen3-coder:latest
EMBEDDING_MODEL_NAME=nomic-embed-text
```

Install dependencies and run:
```bash
# Using uv (recommended)
uv sync
uv run app/main.py

# OR using standard pip
pip install -r requirements.txt
python app/main.py
```
*Backend runs on `http://localhost:8000`*

### 2. Frontend Setup

Navigate to the frontend directory:
```bash
cd medical-rag-frontend
```

Install dependencies and run:
```bash
npm install
npm run dev
```
*Frontend runs on `http://localhost:3000`*

## 💡 Usage

1.  **Open the App**: Go to [http://localhost:3000](http://localhost:3000).
2.  **Upload Documents**: Use the "Upload PDF" button in the sidebar to add medical records.
3.  **Chat**: Ask questions like "What are the side effects of Aspirin?" or "Check interactions for X and Y".
4.  **Health Tracker**: Navigate to "Health Tracker" to log metrics like heart rate (persisted to DB).
5.  **Appointments**: View or schedule new appointments via the chat agent.

## 📁 Project Structure

- `medical-rag-backend/`: FastAPI server, ChromaDB vector store, Ingestion logic.
- `medical-rag-frontend/`: Next.js 14, Tailwind CSS, Shadcn UI components.
- `db/`: Local Chrome vector database (for RAG).
- `.gitignore`: Configured to exclude sensitive and build files.
