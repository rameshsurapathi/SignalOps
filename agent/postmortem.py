"""
agent/postmortem.py

This module contains the logic for the final node in the LangGraph workflow.
It executes only if the human operator approves the proposed fix. 
It now uses the Gemini LLM to synthesize a highly technical Root Cause Analysis.
"""

from langchain_core.messages import AIMessage
from .llm import get_llm

# =====================================================================
# POST-MORTEM GENERATOR
# =====================================================================
async def generate_post_mortem(state: dict):
    """
    Node 5: Generate Post-Mortem
    
    Uses Gemini to synthesize a technical RCA from raw logs and metrics,
    producing a formal Markdown report.
    """
    print("[Agent] Generating final technical post-mortem report...")
    
    service = state.get("service_name", "Unknown Service")
    details = state.get("incident_details", "No detailed context gathered.")
    fix = state.get("proposed_fix", "No fix recorded.")
    applied = state.get("applied_remediation", fix) # Fallback to proposed fix if remediation string is missing
    
    # Use LLM to generate a TECHNICAL RCA based on the context
    llm = get_llm()
    rca_prompt = f"""
    You are a Senior SRE. Based on the following raw diagnostic data for {service}, 
    write a 2-paragraph highly technical Root Cause Analysis (RCA). 
    Include specific mentions of error codes, memory values, or log patterns found in the evidence.
    Be concise but extremely technical.
    
    Diagnostic Data:
    {details}
    """
    
    try:
        rca_response = await llm.ainvoke(rca_prompt)
        # Handle cases where Gemini returns content as a list of dictionaries
        if isinstance(rca_response.content, list):
            rca_text = "".join([c['text'] for c in rca_response.content if isinstance(c, dict) and c.get('type') == 'text'])
        else:
            rca_text = rca_response.content
    except Exception as e:
        rca_text = f"Technical RCA synthesis failed: {e}. Raw data is available in the evidence section."

    # Template the formal incident post-mortem
    report = f"""
### 📄 Technical Incident Post-Mortem: `{service}`

**1. Executive Summary**
Automated investigation confirmed a critical failure in `{service}`. This report was synthesized by SignalOps AI after human verification of the proposed resolution.

**2. Technical Root Cause Analysis**
{rca_text}

**3. Evidence & Raw Diagnostic Data**
<details>
<summary>Click to expand raw tool outputs</summary>
{details}
</details>

**4. Resolution Path**
The following fix was approved by the human operator and executed:
> {applied}

**5. Preventative Action Items**
* **Infrastructure**: Review HPA (Horizontal Pod Autoscaler) settings and resource limits for `{service}`.
* **Observability**: Implement high-cardinality monitoring for the specific failure patterns identified in this RCA.
* **Automation**: Whitelist this specific fix for auto-remediation in future occurrences.
"""
    
    return {"messages": [AIMessage(content=report)]}
