# ✈️ RiskPilot: Corporate Risk Intelligence System

RiskPilot is a robust risk management platform that leverages Multi-Agent AI (Google Gemini) to analyze corporate risks across Employees, Projects, Financials, and Market trends. It ingests corporate data via CSV and provides actionable insights through an interactive dashboard and an AI chat consultant.

## 🚀 Features

*   **Multi-Agent AI Analysis**: Specialized agents for Employee, Project, Financial, and Market risk analysis.
*   **Interactive Dashboard**: Visualizations for project health, budget utilization, and risk probability.
*   **AI Chat Consultant**: specific questions about your project risks and get intelligent responses.
*   **Data Ingestion**: Easy CSV upload for comprehensive analysis.
*   **Modern Tech Stack**: Built with FastAPI, Streamlit, and Supabase.

## 🛠️ Tech Stack

*   **Frontend**: Streamlit (Python), Plotly
*   **Backend**: FastAPI (Python)
*   **Database**: Supabase (PostgreSQL)
*   **AI**: Google Gemini Pro

## 📋 Prerequisites

*   Python 3.9+ installed
*   Supabase Account (Project URL & API Key)
*   Google Gemini API Key

## ⚙️ Installation & Setup

1.  **Clone/Open the project** in your terminal.

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment**:
    *   Windows: `.\venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Variables**:
    Create a `.env` file in the root directory and fill in your keys (see `.env.example`):
    ```env
    SUPABASE_URL="your_url"
    SUPABASE_KEY="your_key"
    GEMINI_API_KEY="your_key"
    ```

6.  **Database Setup**:
    *   Copy the contents of `supabase_schema.sql`.
    *   Run it in your Supabase project's **SQL Editor** to create the tables.

## 🏃‍♂️ How to Run

**Important**: Run these commands from the **root** folder (`risk/`), not inside `backend` or `frontend`.

### 1. Start the Backend (API)
```bash
# Ensure venv is activated
python -m uvicorn backend.main:app --reload
```
The API will run at `http://localhost:8000`.

### 2. Start the Frontend (Dashboard)
Open a **new** terminal, activate `venv`, and run:
```bash
python -m streamlit run frontend/app.py
```
The application will open in your browser at `http://localhost:8501`.

## 📂 Usage

1.  **Add Project**: Navigate to "Add New Project" in the sidebar.
2.  **Upload Data**: Use the sample files in `test_files/` (`employees.csv`, `projects.csv`, `financials.csv`).
3.  **Analyze**: Click "Initialize Project & Run Analysis". Use the Dashboard to view risks and Chat to ask questions.
