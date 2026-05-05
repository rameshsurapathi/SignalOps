# Gemini SignalOps – Autonomous SRE Command Center

**"From 1000 logs → 1 decision → 1 action"**

Gemini SignalOps is an AI-powered SRE agent built for the Google AI Agent Hackathon. It autonomously analyzes system issues using mock logs, metrics, and deployment histories, and provides structured root cause analysis and remediation strategies using **Gemini 1.5 Pro**.

## Architecture
- **FastAPI Backend**: Acts as the Agent Orchestrator.
- **MCP Tools Layer**: Provides mock integrations for logs, metrics, and GitHub deploy history.
- **Gemini 1.5 Pro (Google GenAI SDK)**: Powers the reasoning engine to deduce root causes.
- **Streamlit Frontend**: A simple dashboard to trigger incidents and view the agent's decision flow.

## Project Structure
```
signalops/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── agent.py         # Gemini logic and system prompt
│   └── tools/
│       └── mock_tools.py # Mock implementations of get_logs, get_metrics, etc.
├── ui/
│   └── app.py           # Streamlit dashboard
├── data/                # (Optional) Data persistence
├── docker-compose.yml   # For easy local running
└── requirements.txt     # Python dependencies
```

## Running the Application

### Option 1: Docker Compose (Recommended)
Make sure you have Docker and Docker Compose installed.

1. Set your Gemini API Key in your environment:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
2. Start the services:
   ```bash
   docker-compose up --build
   ```
3. Open Streamlit in your browser at `http://localhost:8501`

### Option 2: Local Python Environment
1. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Export your Gemini API Key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. Run the backend (Terminal 1):
   ```bash
   uvicorn backend.main:app --reload
   ```
4. Run the frontend (Terminal 2):
   ```bash
   streamlit run ui/app.py
   ```

## Hackathon Note
The tools for fetching logs, metrics, and deployments are intentionally mocked to demonstrate the orchestrator's reasoning capabilities without requiring a full production Kubernetes or GCP environment setup.
