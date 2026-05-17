"""
agent/llm.py

This module handles the initialization of the Language Model (LLM) using
Google's Gemini API via Vertex AI.
"""

import os
from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI
from pydantic import BaseModel, Field

# Load API key from .env file
load_dotenv()

# =====================================================================
# ENTERPRISE GUARDRAILS (Structured Outputs)
# =====================================================================
class AlertAnalysisSchema(BaseModel):
    service_name: str = Field(description="The name of the service identified from the alert.")
    required_tools: list[str] = Field(description="List of MCP tools needed to investigate this specific incident type.")
    reasoning: str = Field(description="Brief technical explanation for why these tools were selected.")

class IncidentAnalysisSchema(BaseModel):
    service: str = Field(description="The name of the service being analyzed.")
    issue: str = Field(description="A brief description of the detected incident.")
    root_cause: str = Field(description="The technical root cause of the incident based on evidence.")
    evidence: list[str] = Field(description="List of specific logs, metrics, or events confirming the root cause.")
    proposed_fix: str = Field(description="The actionable step to resolve the incident.")
    required_tools: list[str] = Field(description="The tools that were used during this investigation.")

# =====================================================================
# LLM CONFIGURATION & INITIALIZATION
# =====================================================================
def get_llm(structured: bool = False, schema_type: str = "incident"):
    """
    Initializes and returns the Gemini model via Vertex AI with enterprise guardrails.
    
    Guardrail 1: Temperature = 0.0 (Eliminates creative hallucination)
    Guardrail 2: Strict Pydantic Schema (if structured=True)
    """
    llm = ChatVertexAI(
        model_name="gemini-1.5-flash",
        temperature=0.0,
        max_output_tokens=8192
    )
    
    if structured:
        if schema_type == "alert":
            return llm.with_structured_output(AlertAnalysisSchema)
        return llm.with_structured_output(IncidentAnalysisSchema)
        
    return llm
