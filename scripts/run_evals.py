import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import app_graph
from langchain_core.messages import HumanMessage

# =====================================================================
# EVALUATION SUITE
# =====================================================================
EVAL_CASES = [
    {
        "name": "OOMKill (payment-service)",
        "alert": "Investigate payment-service crash",
        "expected_service": "payment-service",
        "expected_root_cause": "memory",
        "required_tools": ["get_kubernetes_events"]
    },
    {
        "name": "DB Timeout (auth-service)",
        "alert": "Investigate auth-service crash",
        "expected_service": "auth-service",
        "expected_root_cause": "connection pool",
        "required_tools": ["fetch_datadog_logs"]
    },
    {
        "name": "Net Partition (inventory)",
        "alert": "Investigate inventory-service crash",
        "expected_service": "inventory-service",
        "expected_root_cause": "network",
        "required_tools": ["get_kubernetes_events"]
    },
    {
        "name": "Error Rate (api-gateway)",
        "alert": "Investigate api-gateway crash",
        "expected_service": "api-gateway",
        "expected_root_cause": "canary",
        "required_tools": ["query_grafana_metrics"]
    },
    {
        "name": "Bad Config (user-service)",
        "alert": "Investigate user-service crash",
        "expected_service": "user-service",
        "expected_root_cause": "secret",
        "required_tools": ["get_kubernetes_events"]
    }
]

async def run_eval():
    print("🛡️ SignalOps Agent Evaluation Runner")
    print("=" * 40)
    
    results = []
    
    for idx, case in enumerate(EVAL_CASES):
        if idx > 0:
            print("[Evals] Sleeping 6 seconds to respect Gemini API rate limits...")
            await asyncio.sleep(6)
            
        print(f"\n[Case] {case['name']}")
        print(f"[Input] {case['alert']}")
        
        # Initialize graph state
        initial_input = {"messages": [HumanMessage(content=case['alert'])]}
        config = {"configurable": {"thread_id": f"eval-{case['name']}"}}
        
        # Run until hitl_gate
        try:
            final_state = None
            async for event in app_graph.astream(initial_input, config=config):
                final_state = event
            
            # Get actual state from graph
            state = app_graph.get_state(config)
            values = state.values
            
            # Assertions
            service_name = values.get("service_name")
            service_ok = service_name == case["expected_service"]

            # Check the dedicated root_cause field from the structured LLM output,
            # falling back to proposed_fix for resilience.
            rca_text = (values.get("root_cause") or values.get("proposed_fix") or "").lower()
            rca_ok = case["expected_root_cause"].lower() in rca_text

            tools_used = values.get("required_tools", [])
            tools_ok = any(t in tools_used for t in case["required_tools"])

            warnings = values.get("warnings") or []

            print(f"  - Service Identification: {'✅' if service_ok else '❌'} (Got: {service_name})")
            print(f"  - Tool Selection Accuracy: {'✅' if tools_ok else '❌'} (Got: {tools_used})")
            print(f"  - RCA Faithfulness: {'✅' if rca_ok else '❌'} (Looking for '{case['expected_root_cause']}' in root_cause)")
            if warnings:
                for w in warnings:
                    print(f"  - ⚠️  Warning: {w}")

            results.append(service_ok and tools_ok and rca_ok)
        except Exception as e:
            print(f"  - Error: ❌ {e}")
            results.append(False)
            
    print("\n" + "=" * 40)
    print(f"Final Score: {sum(results)}/{len(results)}")
    
if __name__ == "__main__":
    asyncio.run(run_eval())
