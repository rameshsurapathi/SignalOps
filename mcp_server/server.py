import json
import os
import re
from mcp.server.fastmcp import FastMCP

# =====================================================================
# INITIALIZATION
# =====================================================================
# Initialize FastMCP Server.
# FastMCP provides a simple, FastAPI-like interface to create MCP servers.
# We name our simulated server "signalops_simulated_backend".
mcp = FastMCP("signalops_simulated_backend")

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================
def load_fixture(service_name: str):
    """
    Dynamically loads the simulated incident data (fixture) for the requested service.
    
    In a real production environment, this function would not exist.
    Instead, the MCP tool functions below would make live HTTP/API requests.
    """
    fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    try:
        # Scan the fixtures directory for JSON files
        for filename in os.listdir(fixtures_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(fixtures_dir, filename)
                with open(filepath, "r") as f:
                    data = json.load(f)
                    # Return the data if the service name matches
                    if data.get("service") == service_name:
                        return data
        return {"service": "unknown"}
    except Exception:
        # Fallback if directory reading fails
        return {"service": "unknown"}

def validate_service_name(service: str):
    """
    SECURITY GUARDRAIL: Input Validation
    Strictly validates that the service name only contains alphanumeric chars and hyphens.
    This prevents Prompt/Command Injection (e.g., someone passing 'payment-service && rm -rf /').
    """
    if not re.match(r"^[a-zA-Z0-9\-]+$", service):
        raise ValueError(f"Security Alert: Malicious input detected. Invalid service name: {service}")

# =====================================================================
# MCP TOOLS (EXPOSED TO THE LANGGRAPH AGENT)
# =====================================================================

@mcp.tool()
def get_kubernetes_events(service: str) -> str:
    """
    Fetch recent Kubernetes events for a given service.
    
    This tool allows the agent to inspect cluster-level events (like OOMKills, 
    CrashLoopBackOffs, scaling events) associated with the target service.
    """
    validate_service_name(service) # Anti-Injection Guardrail
    
    # Load the simulated data.
    data = load_fixture(service)
    
    # Ensure the requested service matches our simulated incident.
    if data["service"] == service:
        # Return the events list formatted as a JSON string.
        return json.dumps(data.get("kubernetes_events", []), indent=2)
    return "[]"

@mcp.tool()
def query_grafana_metrics(service: str) -> str:
    """
    Query current Grafana metrics for a given service.
    
    This tool provides the agent with current resource utilization metrics
    (e.g., CPU, Memory) to help determine if there are resource exhaustion issues.
    """
    validate_service_name(service) # Anti-Injection Guardrail
    
    # Load the simulated data.
    data = load_fixture(service)
    
    # Check if we have metrics for the requested service.
    if data["service"] == service:
        # Return the metrics formatted as a JSON string.
        return json.dumps(data.get("grafana_metrics", {}), indent=2)
    return "{}"

@mcp.tool()
def fetch_datadog_logs(service: str) -> str:
    """
    Fetch centralized logs from Datadog for a given service.
    
    This tool retrieves application logs. Importantly, it demonstrates
    Context Compression: we read a massive log file but only
    send logs that indicate an issue (WARN, ERROR, FATAL) back to the LLM
    to save tokens and prevent context window bloat.
    """
    validate_service_name(service) # Anti-Injection Guardrail
    
    log_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "logs", f"{service}.log")
    
    try:
        compressed_logs = []
        # We process the file line-by-line so we don't load gigabytes into memory
        with open(log_file_path, "r") as f:
            for line in f:
                # Context Compression Strategy: 
                # Filter out all INFO/DEBUG noise on the server side.
                if "WARN" in line or "ERROR" in line or "FATAL" in line:
                    compressed_logs.append(line.strip())
        
        if not compressed_logs:
            return "No relevant errors found in logs."
            
        return "\n".join(compressed_logs)
    except FileNotFoundError:
        return f"No log file found for service: {service}"

@mcp.tool()
def apply_remediation(service: str) -> str:
    """
    Apply a remediation fix for a given service.
    
    This tool simulates the execution of a fix (e.g., rolling back a deployment, 
    restarting a pod, or adjusting resource limits). It returns a confirmation
    string of the action taken.
    """
    validate_service_name(service)
    
    # Concrete remediation strings per scenario
    remediations = {
        "payment-service": "K8s Patch: Increased memory limits to 512Mi and restarted pods.",
        "auth-service": "DB Config: Flushed connection pool and increased max_connections to 200.",
        "inventory-service": "Network Fix: Updated CoreDNS rules to bypass failing proxy node.",
        "api-gateway": "Rollback: Reverted api-gateway to previous stable image (v1.4.2).",
        "user-service": "K8s Secret: Re-created missing 'db-credentials' secret and triggered rollout."
    }
    
    return remediations.get(service, f"Generic Fix: Restarted {service} instances to clear transient errors.")

@mcp.tool()
def lookup_runbook(service: str) -> str:
    """
    Lookup SRE runbooks for troubleshooting guidance.
    
    This tool simulates a search over a corporate knowledge base (e.g., Vertex AI Search)
    to find relevant remediation steps for the current incident.
    """
    validate_service_name(service)
    runbook_path = os.path.join(os.path.dirname(__file__), "..", "data", "runbooks", "sre_runbooks.md")
    try:
        with open(runbook_path, "r") as f:
            content = f.read()
            # Simple simulation: In a real setup, this would be a semantic search call.
            return content
    except FileNotFoundError:
        return "No runbooks found for the requested query."

# =====================================================================
# SERVER EXECUTION
# =====================================================================
if __name__ == "__main__":
    # Runs the MCP server in STDIO mode (Standard Input/Output mode).
    # This is the standard communication method for MCP servers to talk to clients.
    mcp.run()
