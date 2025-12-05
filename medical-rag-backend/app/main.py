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

app = FastAPI(title="Medical AI Backend")

DB_PATH = "db"
DATA_PATH = "data"
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
DATABASE_URL = os.getenv("DATABASE_URL")

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default_session"
    doc_filters: Optional[List[str]] = None

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
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
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
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        try:
            vector_store = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        except Exception as e:
            return f"Error connecting to database: {str(e)}"

        search_kwargs = {"k": 3}
        
        if doc_filters:
            filters = []
            for doc in doc_filters:
                filters.append({"source": os.path.join(DATA_PATH, doc)})
            
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
    Input should be the patient name and time.
    """
    return f"Appointment confirmed for {patient_name}."

# --- API Endpoints ---

@app.get("/documents")
def list_documents():
    """List all available PDF documents in the data directory."""
    if not os.path.exists(DATA_PATH):
        return {"documents": []}
    files = glob.glob(os.path.join(DATA_PATH, "*.pdf"))
    filenames = [os.path.basename(f) for f in files]
    return {"documents": filenames}

@app.post("/chat")
async def chat(request: QueryRequest):
    # Initialize LLM
    # ReAct works best with a bit of temperature to be creative with thoughts, but 0 is safer for formatting.
    llm = ChatOllama(model=MODEL_NAME, temperature=0, stop=["Observation:"])
    
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
    - If you have the answer, use "Final Answer:".

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
            history = get_chat_history(request.session_id)
            messages = history.messages[-5:]
            for msg in messages:
                role = "User" if msg.type == "human" else "Assistant"
                chat_history_str += f"{role}: {msg.content}\n"
        except Exception as e:
            print(f"Warning: Could not fetch chat history: {e}")

    # Run Agent
    try:
        result = agent_executor.invoke({
            "input": request.query,
            "chat_history": chat_history_str
        })
        
        answer = result["output"]
        
        # Save to history
        if DATABASE_URL:
            try:
                history = get_chat_history(request.session_id)
                history.add_user_message(request.query)
                history.add_ai_message(answer)
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
