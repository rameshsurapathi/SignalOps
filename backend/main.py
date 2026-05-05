from fastapi import FastAPI
from pydantic import BaseModel
from .agent import run_agent
from .tools.mock_tools import execute_action

app = FastAPI(title="Gemini SignalOps API")

class AlertRequest(BaseModel):
    service: str
    message: str = "High Error Rate"

@app.post("/incident")
def handle_incident(alert: AlertRequest):
    alert_dict = alert.model_dump() # Updated to Pydantic V2 method
    result = run_agent(alert_dict)
    return {"decision": result}

@app.post("/fix")
def apply_fix():
    return execute_action("Rollback deployment")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
