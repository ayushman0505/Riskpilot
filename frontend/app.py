import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
import os

# Configuration
# Default to localhost for local dev, but override with env var in production
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="RiskPilot", page_icon="✈️", layout="wide")

# Custom CSS for "professional" look
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def get_projects():
    try:
        response = requests.get(f"{API_URL}/projects/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return []

def create_project(name, description, budget):
    try:
        # Check if backend is alive first
        try:
             res = requests.get(f"{API_URL}/")
             if res.status_code != 200:
                 st.error(f"Backend is running but returned {res.status_code}. Check backend logs.")
                 return None
        except requests.exceptions.ConnectionError:
             st.error("Error: Cannot connect to Backend API. Is it running?")
             return None

        payload = {"name": name, "description": description, "budget": budget}
        # Post to /projects (no trailing slash to be safe, though backend handles both now)
        response = requests.post(f"{API_URL}/projects", json=payload)
        
        if response.status_code == 200:
            return response.json()
        
        st.error(f"Failed to create project: {response.text}")
        print(f"Backend Error: {response.status_code} - {response.text}") # Console log
        return None
    except Exception as e:
        st.error(f"Error creating project: {e}")
        return None

# --- UI Layout ---

st.title(" RiskPilot: Corporate Risk Intelligence")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add New Project"])

if page == "Add New Project":
    st.header("Create New Project")
    
    with st.form("new_project_form"):
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        budget = st.number_input("Budget ($)", min_value=0.0)
        
        st.subheader("Upload Data")
        employee_file = st.file_uploader("Employee Data (CSV)", type=["csv"])
        project_file = st.file_uploader("Project Data (CSV)", type=["csv"])
        financial_file = st.file_uploader("Financial Data (CSV)", type=["csv"])
        
        submitted = st.form_submit_button("Initialize Project & Run Analysis")
        
        if submitted:
            if name and employee_file and project_file and financial_file:
                with st.spinner("Creating Project and Running AI Agents..."):
                    # 1. Create Project
                    project_data = create_project(name, description, budget)
                    
                    if project_data:
                        project_id = project_data["id"]
                        
                        # 2. Upload Files & Init Chat
                        files = {
                            "employee_file": employee_file.getvalue(),
                            "project_file": project_file.getvalue(),
                            "financial_file": financial_file.getvalue()
                        }
                        
                        try:
                            res = requests.post(
                                f"{API_URL}/chat/init/{project_id}",
                                files={
                                    "employee_file": employee_file, 
                                    "project_file": project_file, 
                                    "financial_file": financial_file
                                }
                            )
                            
                            if res.status_code == 200:
                                st.success("Project Initialized Successfully!")
                                st.write("### Initial AI Analysis")
                                st.info(res.json().get("analysis"))
                            else:
                                st.error(f"Analysis Failed: {res.text}")
                        except Exception as e:
                            st.error(f"Upload failed: {e}")
            else:
                st.warning("Please fill all fields and upload all files.")

elif page == "Dashboard":
    projects = get_projects()
    
    if not projects:
        st.info("No projects found. Go to 'Add New Project' to start.")
    else:
        # Select Project
        project_names = {p['name']: p for p in projects}
        selected_name = st.sidebar.selectbox("Select Project", list(project_names.keys()))
        current_project = project_names[selected_name]
        project_id = current_project['id']
        
        st.subheader(f"Project: {selected_name}")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Overview & Risks", "AI Consultant"])
        
        with tab1:
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Budget", f"${current_project.get('budget', 0):,}")
            col2.metric("Actual Spend", f"${current_project.get('actual_spend', 0):,}")
            progress = current_project.get('current_progress', 0)
            col3.metric("Progress", f"{progress}%")
            
            # Dummy Visualizations (since we aren't querying deep stats yet)
            # Fetch Real Stats
            stats = {}
            try:
                 stats_res = requests.get(f"{API_URL}/projects/{project_id}/stats")
                 if stats_res.status_code == 200:
                     stats = stats_res.json()
            except:
                 st.warning("Could not fetch detailed stats.")

            fin_data = stats.get("financials", [])
            emp_data = stats.get("employees", [])

            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("💰 Spend by Category")
                if fin_data:
                    df_fin = pd.DataFrame(fin_data)
                    # Group by category
                    df_cat = df_fin.groupby('category')['amount'].sum().reset_index()
                    
                    fig_bar = px.bar(df_cat, x='category', y='amount', 
                                     color='category', 
                                     title="Expenditure Breakdown",
                                     text_auto='.2s')
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("No financial records found.")
                
            with col_b:
                st.subheader("👥 Team Roles")
                if emp_data:
                    df_emp = pd.DataFrame(emp_data)
                    # Count roles
                    df_roles = df_emp['role'].value_counts().reset_index()
                    df_roles.columns = ['role', 'count']
                    
                    fig_pie = px.pie(df_roles, values='count', names='role', hole=0.4, title="Role Distribution")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("No team members found.")
            
            # Additional Row for Gauge
             # Calculate metric based on real updated spend
            spend = current_project.get('actual_spend', 0)
            budget = current_project.get('budget', 1) 
            if budget <= 0: budget = 1
            risk_score = min(round((spend / budget) * 100, 1), 100)

            st.write("### 📉 Project Health")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = risk_score, 
                title = {'text': "Budget Burn Rate (%)"},
                gauge = {'axis': {'range': [None, 100]},
                            'bar': {'color': "red" if risk_score > 90 else "green"},
                            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with tab2:
            st.write("### Chat with RiskPilot")
            
            # Fetch History
            try:
                chat_res = requests.get(f"{API_URL}/chats/{project_id}")
                if chat_res.status_code == 200:
                    history = chat_res.json()
                    for msg in history:
                        with st.chat_message("user" if msg['message'] != "System: Initial Risk Analysis" else "ai"): # Logic check needed, assume stored differenlty or just labeled? 
                            # Actually our DB stores 'message' (user) and 'response' (AI) in same row
                            if msg.get('message') and msg.get('message') != "System: Initial Risk Analysis":
                                st.write(f"**User**: {msg['message']}")
                            st.write(f"**RiskPilot**: {msg['response']}")
                            st.divider()
            except Exception as e:
                st.error("Could not load chat history")

            # Chat Input
            user_input = st.chat_input("Ask about project risks...")
            if user_input:
                # Display user message immediately
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Send to API
                with st.spinner("Analyzing..."):
                    try:
                        payload = {"message": user_input}
                        resp = requests.post(f"{API_URL}/chat/continue/{project_id}", json=payload)
                        if resp.status_code == 200:
                            ai_reply = resp.json().get("response")
                            with st.chat_message("ai"):
                                st.write(ai_reply)
                        else:
                            st.error("Failed to get response")
                    except Exception as e:
                        st.error(f"Error: {e}")
