import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool, render_text_description
from langchain_postgres import PostgresChatMessageHistory
from typing import Optional, List
import glob
import psycopg
from datetime import datetime
from dotenv import load_dotenv

# Load env variables from parent directory if not found
load_dotenv(dotenv_path="../.env")

# --- Configuration ---
import sys
# Add parent directory to path to import ingest.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import ingest_documents, DATA_PATH, DB_PATH

MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-coder:latest")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Database Setup ---
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set.")
    return psycopg.connect(DATABASE_URL)

def init_db():
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not set, skipping DB init.")
        return
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Health Metrics Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS health_metrics (
                        id SERIAL PRIMARY KEY,
                        patient_id TEXT DEFAULT 'default_user',
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                # Appointments Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS appointments (
                        id SERIAL PRIMARY KEY,
                        patient_name TEXT NOT NULL,
                        appointment_time TEXT NOT NULL,
                        status TEXT DEFAULT 'scheduled',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize DB on startup
init_db()

app = FastAPI(title="Medical AI Backend")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev, or specific ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"
    doc_filters: Optional[List[str]] = None

class HealthMetric(BaseModel):
    metric_type: str
    value: float
    unit: str

class AppointmentRequest(BaseModel):
    patient_name: str
    appointment_time: str

def get_chat_history(session_id: str):
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set.")
    return PostgresChatMessageHistory(
        connection_string=DATABASE_URL,
        session_id=session_id,
        table_name="chat_history",
        sync_connection=True
    )

# --- Tools ---

@tool
def search_medical_records(query: str) -> str:
    """
    Search the medical knowledge base (PDFs) for information. 
    Use this tool to answer questions about medical guidelines, prescriptions, or patient history 
    contained in the uploaded documents.
    """
    # Note: ReAct agent struggles with complex arguments like lists. 
    # We will rely on the global/context filters or simplified input.
    # For this implementation, we'll assume the agent passes the query string.
    # We will inject the filters from the request context if possible, 
    # but `tool` functions don't easily access request context without global vars or binding.
    # To keep it simple for ReAct: The agent searches, and we (the code) apply the filters 
    # that were passed to the API. 
    # BUT: The tool execution happens inside the agent. 
    # We need to bind the filters or use a closure.
    # Let's use a global var hack for the demo or a class-based tool.
    # Better: We'll assume the agent just searches text.
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
    try:
        vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    except Exception as e:
        return f"Error connecting to database: {str(e)}"

    search_kwargs = {"k": 3}
    
    # Context-aware filtering hack for demo:
    # In a real app, we'd use RunnableConfig or a class-based tool initialized per request.
    # For this demo, let's look at the `active_filters` global if set, or just search all.
    # Since FastAPI is async, globals are risky. 
    # Let's try to parse filters from the query string if the agent puts them there? No.
    # Let's just search all for now to fix the crash, or rely on the agent finding the right doc by content.
    # OR: We can define the tool *inside* the chat endpoint to capture `request.doc_filters`.
    
    # Let's define the logic here, but we'll actually create the tool instance inside the endpoint 
    # to capture the filters.
    pass 

def create_search_tool(doc_filters: Optional[List[str]]):
    @tool
    def search_tool(query: str) -> str:
        """
        Search the medical knowledge base (PDFs) for information. 
        Use this tool to answer questions about medical guidelines, prescriptions, or patient history.
        """
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
        try:
            vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        except Exception as e:
            return f"Error connecting to database: {str(e)}"

        search_kwargs = {"k": 6}
        
        if doc_filters:
            filters = []
            for doc in doc_filters:
                # The DB stores paths relative to the ingestion root (e.g., "data\file.pdf")
                # We need to match that exactly.
                # Since we are on Windows, we should likely use os.path.join("data", doc)
                # But to be safe and match the DB inspection result:
                filters.append({"source": os.path.join("data", doc)})
            
            if len(filters) == 1:
                search_kwargs["filter"] = filters[0]
            elif len(filters) > 1:
                search_kwargs["filter"] = {"$or": filters}

        retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant information found."
        
        result = ""
        for doc in docs:
            source = os.path.basename(doc.metadata.get("source", "Unknown"))
            result += f"--- Source: {source} ---\n{doc.page_content}\n\n"
        
        return result
    return search_tool

@tool
def check_drug_interactions(drug_list: str) -> str:
    """
    Check for interactions between a list of drugs.
    Input should be a comma-separated list of drug names (e.g., "Aspirin, Warfarin").
    """
    drugs = [d.strip().lower() for d in drug_list.split(",")]
    if "aspirin" in drugs and "warfarin" in drugs:
        return "WARNING: Major interaction detected. Aspirin increases the risk of bleeding when taken with Warfarin."
    if "ibuprofen" in drugs and "lisinopril" in drugs:
        return "CAUTION: Ibuprofen may reduce the effectiveness of Lisinopril and increase risk of kidney damage."
    return "No known major interactions found for these drugs."

@tool
def schedule_appointment(patient_name: str) -> str:
    """
    Schedule a medical appointment.
    Input should be the patient name and time (e.g., "John Doe at 5pm").
    """
    try:
        # Simple parsing logic (in a real app, use an LLM or robust parser)
        parts = patient_name.split(" at ")
        if len(parts) == 2:
            name, time = parts[0], parts[1]
        else:
            name, time = patient_name, "Unspecified Time"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO appointments (patient_name, appointment_time) VALUES (%s, %s)",
                    (name, time)
                )
                conn.commit()
        return f"Appointment confirmed for {name} at {time}."
    except Exception as e:
        return f"Failed to schedule appointment: {e}"

# --- API Endpoints ---

from fastapi import File, UploadFile
import shutil

@app.get("/documents")
def list_documents():
    """List all available PDF documents in the data directory."""
    if not os.path.exists(DATA_PATH):
        return {"documents": []}
    files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    filenames = [os.path.basename(f) for f in files]
    return {"documents": filenames}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        
        file_path = os.path.join(DATA_PATH, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Trigger ingestion (re-index all files to be safe)
        # Note: This is a blocking operation and might timeout for large files.
        # Ideally, use background tasks.
        # But for this demo, generic blocking is "okay" or we can trigger it in background.
        # Fastapi BackgroundTasks is better.
        ingest_documents(clear_db=True)
        
        return {"status": "success", "filename": file.filename, "message": "File uploaded and ingested."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health-metrics")
def get_health_metrics():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT metric_type, value, unit, timestamp FROM health_metrics ORDER BY timestamp DESC")
                rows = cur.fetchall()
                metrics = [{"metric": r[0], "value": r[1], "unit": r[2], "date": r[3]} for r in rows]
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/health-metrics")
def add_health_metric(metric: HealthMetric):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO health_metrics (metric_type, value, unit) VALUES (%s, %s, %s)",
                    (metric.metric_type, metric.value, metric.unit)
                )
                conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments")
def get_appointments():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT patient_name, appointment_time, status, created_at FROM appointments ORDER BY created_at DESC")
                rows = cur.fetchall()
                appointments = [{"patient": r[0], "time": r[1], "status": r[2], "created": r[3]} for r in rows]
        return {"appointments": appointments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/usage-stats")
def get_usage_stats():
    try:
        # Simple usage stats from chat_history table (created by LangChain)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if table exists first
                cur.execute("SELECT to_regclass('public.chat_history');")
                if not cur.fetchone()[0]:
                    return {"total_messages": 0, "unique_sessions": 0}
                
                cur.execute("SELECT COUNT(*) FROM chat_history")
                total_messages = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(DISTINCT session_id) FROM chat_history")
                unique_sessions = cur.fetchone()[0]
                
        return {"total_messages": total_messages, "unique_sessions": unique_sessions}
    except Exception as e:
        # Table might not exist yet if no chats happened
        return {"total_messages": 0, "unique_sessions": 0, "error": str(e)}

@app.post("/chat")
async def chat(request: QueryRequest):
    # Initialize LLM
    # ReAct works best with a bit of temperature to be creative with thoughts, but 0 is safer for formatting.
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    
    # Create the search tool with current filters
    search_tool_instance = create_search_tool(request.doc_filters)
    
    tools = [search_tool_instance, check_drug_interactions, schedule_appointment]
    
    # ReAct Prompt Template - Simplified and stricter
    template = """You are a Medical AI Companion. Answer the following questions as best you can.
    
    You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    IMPORTANT: 
    - Always start your response with "Thought:".
    - Do not output "Observation:" yourself.
    - If you have the answer or do not need to use a tool, you MUST use the format:
      Thought: I have the answer.
      Final Answer: [your response here]
    - Do NOT use "Action: None" or "Action: N/A". If no tool is needed, go straight to Final Answer.
    - When using 'search_tool', your Action Input must be a specific search query (e.g., "patient diagnosis", "blood test results", "medical history summary"). Do NOT use generic terms like "the pdf" or "uploaded file".
    - If your search returns "No relevant information found", DO NOT RETRY EXACTLY THE SAME QUERY. Try a different query or keywords.
    - If you cannot find the answer after 2 different searches, you MUST stop and say: "Final Answer: The provided documents do not contain sufficient information to answer this question."

    Begin!

    Chat History:
    {chat_history}

    Question: {input}
    Thought:{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)
    
    agent = create_react_agent(llm, tools, prompt)
    
    def handle_errors(error) -> str:
        # If the model outputs a response that isn't a tool call but looks like an answer, return it.
        error_str = str(error)
        if "Could not parse LLM output" in error_str:
            # Try to extract the text if it was just a formatting issue
            # Usually the error message contains the output.
            # For now, just ask the model to retry or return a generic message.
            return "I apologize, but I encountered an error processing my thought process. Could you please rephrase?"
        return f"Error: {error_str}"

    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True, # This attempts to auto-fix
        max_iterations=5 # Prevent infinite loops
    )

    # Fetch History
    chat_history_str = ""
    if DATABASE_URL:
        try:
            get_chat_history(request.session_id)
            # We need to manually query because PostgresChatMessageHistory interface might be tricky 
            # or just rely on the object if constructed correctly.
            # Actually, let's fix the construction first.
        except:
            pass
            
        # Re-implementing history fetch manually to be safe or fixing the object usage
        # Ideally we use the object.
        pass

    # Run Agent
    try:
        # We need to manage history string manually for the prompt
        # Let's try to get it from the DB
        chat_history_str = ""
        if DATABASE_URL:
             with get_db_connection() as conn:
                with conn.cursor() as cur:
                     # Check table first
                    try:
                        cur.execute("SELECT type, content FROM chat_history WHERE session_id = %s ORDER BY id DESC LIMIT 5", (request.session_id,))
                        rows = cur.fetchall()
                        # rows are (type, content) - reversed order
                        for r in reversed(rows):
                            role = "User" if r[0] == "human" else "Assistant"
                            chat_history_str += f"{role}: {r[1]}\n"
                    except:
                        pass # Table likely doesn't exist yet

        result = agent_executor.invoke({
            "input": request.query,
            "chat_history": chat_history_str
        })
        
        answer = result["output"]
        
        # Save to history
        if DATABASE_URL:
            try:
                # Use the class but fix arguments? 
                # Or just manual insert since we are already doing manual fetch?
                # Manual insert is safer given the warnings.
                 with get_db_connection() as conn:
                    with conn.cursor() as cur:
                        # Create table if not exists (handled by init_db? No, LangChain creates it usually)
                        # Let's create it manually to be sure.
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS chat_history (
                                id SERIAL PRIMARY KEY,
                                session_id TEXT NOT NULL,
                                type TEXT NOT NULL,
                                content TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                        """)
                        cur.execute(
                            "INSERT INTO chat_history (session_id, type, content) VALUES (%s, %s, %s)",
                            (request.session_id, "human", request.query)
                        )
                        cur.execute(
                            "INSERT INTO chat_history (session_id, type, content) VALUES (%s, %s, %s)",
                            (request.session_id, "ai", answer)
                        )
                        conn.commit()

            except Exception as e:
                print(f"Warning: Could not save to chat history: {e}")

        return {
            "answer": answer,
            "source_documents": [] 
        }
    except Exception as e:
        # Fallback if agent fails completely
        print(f"Agent failed: {e}")
        return {
            "answer": "I apologize, but I'm having trouble processing that request right now. Please try again.",
            "source_documents": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
