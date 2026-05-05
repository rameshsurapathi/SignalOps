def get_logs(service: str):
    return """
    ERROR: CrashLoopBackOff in payment-service
    Reason: Missing ENV DB_URL
    """

def get_metrics(service: str):
    return {"cpu": "85%", "memory": "92%"}

def get_recent_deploys(service: str):
    return "Last deploy 10 mins ago by commit abc123"

def execute_action(action: str):
    return f"Executed: {action}"

def compress_logs(logs: str):
    if "CrashLoopBackOff" in logs and "DB_URL" in logs:
        return "CrashLoopBackOff due to missing DB_URL"
    return logs.strip()

def get_cost_impact(action: str):
    if "scale" in action.lower():
        return "+$200/month"
    return "$0"
