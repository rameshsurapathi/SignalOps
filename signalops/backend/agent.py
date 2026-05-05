import os
from google import genai
from google.genai import types
from .tools.mock_tools import get_logs, get_metrics, get_recent_deploys, compress_logs, get_cost_impact

# Memory (Simple but powerful)
memory = {
    "CrashLoopBackOff": "Fix: Add missing env variable DB_URL"
}

SYSTEM_PROMPT = """You are a Senior Site Reliability Engineer (SRE).

Your job:
- Analyze system issues using logs, metrics, and deploy history
- Identify root cause
- Provide a single best action

IMPORTANT RULES:
- Be extremely concise (Clean, 3-5 lines max)
- Do NOT output logs
- No noise, output ONLY the structured format exactly as below

FORMAT:
Issue:
Root Cause:
Confidence:
Fix:
Cost Impact:"""

def run_agent(alert):
    raw_logs = get_logs(alert["service"])
    logs = compress_logs(raw_logs)  # Context Compression
    metrics = get_metrics(alert["service"])
    deploy = get_recent_deploys(alert["service"])
    
    # Simple Memory Check
    past_knowledge = ""
    for issue_key, known_fix in memory.items():
        if issue_key in logs:
            past_knowledge += f"\nMEMORY: This issue occurred before. Applying known fix: {known_fix}"

    # We provide the cost function directly into context so Gemini knows the cost impact
    # In a real app, Gemini would use function calling to evaluate the fix cost before finalizing.
    cost_info = "Cost Context: Scaling operations cost +$200/month. Config changes cost $0."

    context = f"""
    Alert: {alert}
    Compressed Logs: {logs}
    Metrics: {metrics}
    Deploy: {deploy}
    {past_knowledge}
    {cost_info}
    """

    # We initialize inside the function so it doesn't crash on import if key is missing
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable not set."
        
    client = genai.Client()
    
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents=context,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
        )
    )
    return response.text
