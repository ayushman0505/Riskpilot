import os
import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional
import uuid
from datetime import datetime

# Import our models and agents
from backend.models import ProjectCreate, ProjectResponse, ChatRequest, ChatResponse, InitialAnalysisResponse
from backend.agent import (
    EmployeeRiskAgent, 
    ProjectTrackingAgent, 
    FinancialAgent, 
    MarketAnalysisAgent, 
    MasterAgent
)

load_dotenv()

app = FastAPI(title="RiskPilot API", description="Backend for Corporate Risk Intelligence System")

# Initialize Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: Supabase URL or Key not found in environment variables.")

supabase: Client = create_client(url, key) if url and key else None

# --- Helpers ---
def get_db():
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    return supabase

# --- Endpoints ---

@app.on_event("startup")
def startup_event():
    print("Startup: Registered Routes:")
    for route in app.routes:
        print(f" - {route.path} [{route.methods}]")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "RiskPilot API is running"}

@app.post("/projects", response_model=ProjectResponse) # Support no trailing slash
@app.post("/projects/", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    """Create a new project entry in the database."""
    print(f"Creating project: {project.name}")
    data = project.model_dump(exclude_unset=True)
    try:
        response = get_db().table("projects").insert(data).execute()
        if response.data:
            print("Project created successfully.")
            return response.data[0]
        print("Supabase returned no data.")
        raise HTTPException(status_code=400, detail="Failed to create project - No data returned")
    except Exception as e:
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@app.get("/projects", response_model=List[ProjectResponse])
@app.get("/projects/", response_model=List[ProjectResponse])
def list_projects():
    """List all projects."""
    try:
        response = get_db().table("projects").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/init/{project_id}")
async def init_chat(
    project_id: uuid.UUID,
    employee_file: UploadFile = File(...),
    project_file: UploadFile = File(...),
    financial_file: UploadFile = File(...)
):
    """
    Initialize the AI analysis:
    1. Parse CSVs
    2. Save data to Supabase (simplified for demo)
    3. Run Multi-Agent Analysis
    """
    try:
        # 1. Read Files
        emp_df = pd.read_csv(io.StringIO(str(await employee_file.read(), 'utf-8')))
        proj_df = pd.read_csv(io.StringIO(str(await project_file.read(), 'utf-8')))
        fin_df = pd.read_csv(io.StringIO(str(await financial_file.read(), 'utf-8')))

        # 2. Convert to string for AI context
        emp_text = emp_df.to_string(index=False)
        proj_text = proj_df.to_string(index=False)
        fin_text = fin_df.to_string(index=False)

        # 3. Calculate Real Financial Aggregates
        try:
            # Clean 'amount' column (remove currency symbols if any) and sum
            if 'amount' in fin_df.columns:
                 # Check if project_name column exists to filter? 
                 # For now, simplistic sum of the uploaded file
                 total_spend = pd.to_numeric(fin_df['amount'], errors='coerce').sum()
                 total_spend = float(total_spend) # Ensure native python float
                 
                 print(f"Calculated Total Spend: {total_spend}")
                 
                 # Update Supabase
                 get_db().table("projects").update({"actual_spend": total_spend}).eq("id", str(project_id)).execute()
            else:
                 print("Warning: 'amount' column not found in financials CSV")
        except Exception as e:
            print(f"Error Aggregating Financials: {e}")

        # --- NEW: RAG Ingestion Pipeline ---
        try:
            from backend.agent import rag_system
            
            # 1. Clean old vectors
            rag_system.clean_project_data(str(project_id))
            
            # 2. Ingest Files
            count = 0
            if not proj_df.empty:
                count += rag_system.ingest_csv(proj_df.to_csv(index=False), {"project_id": str(project_id), "type": "Projects"})
                
            if not emp_df.empty:
                count += rag_system.ingest_csv(emp_df.to_csv(index=False), {"project_id": str(project_id), "type": "Employees"})
                
            if not fin_df.empty:
                count += rag_system.ingest_csv(fin_df.to_csv(index=False), {"project_id": str(project_id), "type": "Financials"})
                
            print(f"✅ RAG Ingestion Complete. {count} chunks indexed.")
            
        except Exception as e:
            print(f" RAG Ingestion Failed: {e}")
        # -----------------------------------
        
        # 4. Run Agents
        emp_agent = EmployeeRiskAgent()
        proj_agent = ProjectTrackingAgent()
        fin_agent = FinancialAgent()
        market_agent = MarketAnalysisAgent()
        master_agent = MasterAgent()

        emp_analysis = emp_agent.analyze(emp_text)
        proj_analysis = proj_agent.analyze(proj_text)
        fin_analysis = fin_agent.analyze(fin_text)
        market_analysis = market_agent.analyze(f"Project ID: {project_id}\nDetails: {proj_text}")

        final_report = master_agent.synthesize(
            emp_analysis, proj_analysis, fin_analysis, market_analysis
        )

        # 5. Save Analysis to Chat History
        chat_entry = {
            "project_id": str(project_id),
            "message": "System: Initial Risk Analysis",
            "response": final_report
        }
        get_db().table("chat_history").insert(chat_entry).execute()

        return {"analysis": final_report}

    except Exception as e:
        print(f"Error in init_chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.post("/chat/continue/{project_id}")
def chat_continue(project_id: uuid.UUID, request: ChatRequest):
    """Continue conversation with context."""
    try:
        # Retrieve history
        history_response = get_db().table("chat_history").select("*").eq("project_id", str(project_id)).order("timestamp").execute()
        history = history_response.data

        # Simple context retrieval (in production, use vector store or refined query)
        # For now, we assume the AI has 'memory' via the history or we re-fetch basics.
        # To keep it simple, we just pass the history to the agent.
        
        master_agent = MasterAgent()
        # We might need to fetch project data again if we don't store it in context, 
        # but for this flow let's rely on history or a generic prompt for now.
        context_data = "Refer to previous analysis." 
        
        # Updated to pass project_id for Caching
        ai_response = master_agent.chat(request.message, history, str(project_id))

        # Save to DB
        new_entry = {
            "project_id": str(project_id),
            "message": request.message,
            "response": ai_response
        }
        get_db().table("chat_history").insert(new_entry).execute()

        return {"response": ai_response, "timestamp": datetime.now()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/{project_id}")
def get_chat_history(project_id: uuid.UUID):
    try:
        response = get_db().table("chat_history").select("*").eq("project_id", str(project_id)).order("timestamp").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
