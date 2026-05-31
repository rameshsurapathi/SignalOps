# 🚀 SignalOps Demo Guide

This document outlines the five simulated incident scenarios included in the SignalOps hackathon prototype.

## 📋 Scenario Overview

| Service | Incident Type | Diagnostic Tools Used | Expected Remediation |
| :--- | :--- | :--- | :--- |
| **payment-service** | OOMKill | K8s Events, Metrics, Runbook | Memory limit increase |
| **auth-service** | DB Timeout | Logs, Metrics, Runbook | Connection pool flush |
| **inventory-service** | Net Partition | K8s Events, Logs | CoreDNS rule update |
| **api-gateway** | Error Rate Spike | Metrics, Logs | Deployment rollback |
| **user-service** | Bad Config | K8s Events | Secret re-creation |

---

## 🛠️ Step-by-Step Demo Instructions

1.  **Launch the UI:** `streamlit run ui/app.py`
2.  **Select a Scenario:** Click one of the "🚨" buttons to trigger an alert.
3.  **Watch Reasoning:** Observe the agent:
    *   **Analyze:** Identifying the service and selecting tools via Gemini 1.5 Flash.
    *   **Gather:** Executing MCP tools and compressing logs.
    *   **Propose:** Generating a structured fix side-by-side with raw evidence.
4.  **HITL Approval:** Review the proposed fix and click **"Approve Fix"**.
5.  **Final Report:** View the technical Post-Mortem with the actual remediation confirmation.

---

## 🛡️ Automated Evaluation
Judges can verify the agent's consistency by running the evaluation suite:

```bash
python scripts/run_evals.py
```
This script tests all 5 scenarios and asserts on:
*   **Service Identification** (Correct target detected)
*   **Tool Selection** (Appropriate diagnostic tools picked)
*   **RCA Faithfulness** (Technical root cause identified correctly)

---

## 🔍 What to Look For (For Judges)
*   **Gemini API Integration:** The agent uses `gemini-3.5-flash` via Google AI Studio for all reasoning steps.
*   **MCP Protocol:** Standardized tool discovery and execution.
*   **Side-by-Side Dashboard:** Clear visualization of AI-driven synthesis vs. raw infrastructure data.
*   **HITL Safety:** Strict gatekeeping before infrastructure changes.
*   **2-Min Demo Video:** Playable demo file `output.mp4` in the root directory showcasing the end-to-end user workflow.
