import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class BaseAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        if not GROQ_API_KEY:
            print("Error: GROQ_API_KEY not found.")
            self.client = None
        else:
            self.client = Groq(api_key=GROQ_API_KEY)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        if not self.client:
            return "Error: AI not configured. Please add GROQ_API_KEY to .env"
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

class EmployeeRiskAgent(BaseAgent):
    def analyze(self, employee_data: str) -> str:
        prompt = f"""
        You are an Expert Employee Risk Analyst. 
        Analyze the following employee data for attrition risk, performance issues, and attendance patterns.
        Highlight any high-risk employees and suggest mitigation strategies.
        
        Data:
        {employee_data}
        
        Analysis:
        """
        return self.generate(prompt)

class ProjectTrackingAgent(BaseAgent):
    def analyze(self, project_data: str) -> str:
        prompt = f"""
        You are a Senior Project Manager.
        Analyze the following project data regarding deadlines, milestones, and schedule variance.
        Identify any projects at risk of delay and recommend corrective actions.
        
        Data:
        {project_data}
        
        Analysis:
        """
        return self.generate(prompt)

class FinancialAgent(BaseAgent):
    def analyze(self, financial_data: str) -> str:
        prompt = f"""
        You are a Corporate Financial Auditor.
        Analyze the following financial records for budget overruns, spending anomalies, and ROI concerns.
        Compare actual spend vs budget if available.
        
        Data:
        {financial_data}
        
        Analysis:
        """
        return self.generate(prompt)

class MarketAnalysisAgent(BaseAgent):
    def analyze(self, context: str) -> str:
        prompt = f"""
        You are a Market Risk Strategist.
        Based on the current general market trends (using your internal knowledge) and the specific project context provided below,
        analyze potential market risks that could impact this project.
        
        Context:
        {context}
        
        Analysis:
        """
        return self.generate(prompt)

class MasterAgent(BaseAgent):
    def synthesize(self, employee_analysis: str, project_analysis: str, financial_analysis: str, market_analysis: str) -> str:
        prompt = f"""
        You are the Chief Risk Officer (CRO) of a major corporation.
        Synthesize the following specific risk analyses into a comprehensive Executive Risk Report.
        Prioritize the most critical risks that need immediate attention.
        
        Employee Risk Analysis:
        {employee_analysis}
        
        Project Schedule Analysis:
        {project_analysis}
        
        Financial Analysis:
        {financial_analysis}
        
        Market Risk Analysis:
        {market_analysis}
        
        Executive Summary & Action Plan:
        """
        return self.generate(prompt)

    def chat(self, user_message: str, history: list, context_data: str) -> str:
        # Construct messages with history
        messages = [
            {"role": "system", "content": f"You are RiskPilot, an AI Risk Intelligence System.\nProject Context:\n{context_data}"}
        ]
        
        # Add history (simple mapping)
        for msg in history:
            role = "assistant" if msg['message'] == "System: Initial Risk Analysis" else "user" 
            # Note: Our DB schema might need better role separation, but for now:
            # Check if it was me (assistant) or user. 
            # In our main.py, we stored user msg in 'message' and AI reply in 'response'. 
            # So we append both.
            messages.append({"role": "user", "content": msg['message']})
            messages.append({"role": "assistant", "content": msg['response']})
            
        messages.append({"role": "user", "content": user_message})

        if not self.client:
             return "Error: AI Config Missing"

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
