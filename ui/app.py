"""
ui/app.py

This module provides the Streamlit frontend for the Universal Agent.
It connects to the LangGraph workflow, displays intermediate reasoning steps,
and provides the vital Human-In-The-Loop (HITL) gate for approving fixes.
"""

import streamlit as st
import time
import asyncio
from langchain_core.messages import HumanMessage
import sys
import os

# Add the parent directory to the path so we can import 'agent'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.graph import build_graph

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="SignalOps SRE Agent", 
    page_icon="🛡️", 
    layout="wide"
)

# Create a professional central layout
_, main_col, _ = st.columns([1, 10, 1])

with main_col:
    st.title("🛡️ SignalOps Universal SRE Agent")
    st.markdown("Powered by LangGraph, Vertex AI, and Model Context Protocol (MCP)")

    # =====================================================================
    # CUSTOM CSS (Premium Aesthetics)
    # =====================================================================
    st.markdown("""
        <style>
        /* Main Background & Light Theme Font */
        .stApp {
            background-color: #f9fafb;
            color: #1f2937;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Header Styling */
        h1 {
            color: #111827;
            font-weight: 800;
            letter-spacing: -0.025em;
        }

        /* Info & Success Boxes (Light Theme) */
        div.stAlert {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            color: #374151;
        }

        /* Primary Action Buttons */
        .stButton > button {
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            color: #374151;
        }
        
        .stButton > button:hover {
            border-color: #3b82f6;
            color: #3b82f6;
            background-color: #eff6ff;
        }

        /* Post-Mortem Report Styling (Clean Alignment) */
        .post-mortem-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 40px;
            border-radius: 12px;
            margin-top: 24px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            width: 100% !important;
            display: block;
        }

        .post-mortem-header {
            color: #111827;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 24px;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 12px;
            width: 100%;
        }
        
        /* Code blocks in light mode */
        code {
            color: #2563eb !important;
            background-color: #f3f4f6 !important;
            padding: 2px 4px;
            border-radius: 4px;
        }

        /* Alignment Fix for the container */
        [data-testid="stMarkdownContainer"] {
            width: 100% !important;
        }
        
        [data-testid="stVerticalBlock"] > div:has(div.post-mortem-card) {
            width: 100% !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # =====================================================================
    # SESSION STATE INITIALIZATION
    # =====================================================================
    if "app_graph" not in st.session_state:
        st.session_state.app_graph = build_graph()
        
    if "thread_config" not in st.session_state:
        st.session_state.thread_config = {"configurable": {"thread_id": "incident-8492"}}
        
    if "workflow_paused" not in st.session_state:
        st.session_state.workflow_paused = False

    if "messages_ui" not in st.session_state:
        st.session_state.messages_ui = []

    if "raw_context" not in st.session_state:
        st.session_state.raw_context = ""
    
    if "proposed_fix_ui" not in st.session_state:
        st.session_state.proposed_fix_ui = ""

    # Helper function to display messages
    def show_messages():
        for msg in st.session_state.messages_ui:
            st.info(msg)
        
        if st.session_state.raw_context and st.session_state.proposed_fix_ui:
            st.divider()
            st.subheader("🔍 Investigation Dashboard: Raw Evidence vs. AI Synthesis")
            col_raw, col_synth = st.columns(2)
            
            with col_raw:
                st.markdown("### 🛠️ Raw Diagnostic Data (MCP)")
                st.code(st.session_state.raw_context, language="text")
                
            with col_synth:
                st.markdown("### 🧠 AI Root Cause Analysis")
                st.success(st.session_state.proposed_fix_ui)

    # =====================================================================
    # MAIN WORKFLOW: INGEST ALERT
    # =====================================================================
    st.header("1. Alert Ingestion")

    st.markdown("Choose a simulated incident to investigate:")
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)

    incident_request = None

    with col1:
        if st.button("🚨 OOMKill (payment-service)", use_container_width=True):
            incident_request = "Investigate payment-service crash"

    with col2:
        if st.button("🚨 DB Timeout (auth-service)", use_container_width=True):
            incident_request = "Investigate auth-service crash"

    with col3:
        if st.button("🚨 Net Partition (inventory)", use_container_width=True):
            incident_request = "Investigate inventory-service crash"

    with col4:
        if st.button("🚨 API Error Rate (api-gateway)", use_container_width=True):
            incident_request = "Investigate api-gateway crash"

    with col5:
        if st.button("🚨 Bad Config (user-service)", use_container_width=True):
            incident_request = "Investigate user-service crash"


    if incident_request:
        st.session_state.messages_ui = []
        st.session_state.raw_context = ""
        st.session_state.proposed_fix_ui = ""
        st.session_state.workflow_paused = False
        
        st.session_state.messages_ui.append("Alert received. Agent initiated investigation...")
        
        # Initialize the graph with a human request
        initial_input = {"messages": [HumanMessage(content=incident_request)]}
        
        async def run_agent():
            # Stream the graph execution asynchronously
            with st.spinner("Agent is dynamically gathering context via MCP tools..."):
                async for event in st.session_state.app_graph.astream(initial_input, config=st.session_state.thread_config):
                    for node_name, state_update in event.items():
                        st.session_state.messages_ui.append(f"✅ Executed step: **{node_name}**")

                        if state_update and state_update.get("warnings"):
                            for w in state_update["warnings"]:
                                st.session_state.messages_ui.append(f"⚠️ **Warning:** {w}")

                        if state_update and "incident_details" in state_update:
                            st.session_state.raw_context = state_update['incident_details']

                        if state_update and "proposed_fix" in state_update:
                            st.session_state.proposed_fix_ui = state_update['proposed_fix']

            # Check the graph's current state to see if it paused at hitl_gate
            state = st.session_state.app_graph.get_state(st.session_state.thread_config)
            if state.next and "hitl_gate" in state.next:
                st.session_state.workflow_paused = True

        # Run the async loop
        asyncio.run(run_agent())

    show_messages()

    # =====================================================================
    # HITL GATE: HUMAN APPROVAL
    # =====================================================================
    if st.session_state.workflow_paused:
        st.divider()
        st.subheader("⏸️ Human-In-The-Loop Approval Required")
        st.markdown("The agent has proposed a fix but cannot execute it without operator approval.")
        
        col1, col2 = st.columns(2)
        
        approve_clicked = False
        reject_clicked = False
        
        with col1:
            # Operator Approves the Fix
            if st.button("✅ Approve Fix & Generate Post-Mortem", use_container_width=True):
                approve_clicked = True

        with col2:
            # Operator Rejects the Fix
            if st.button("❌ Reject Fix", use_container_width=True, type="primary"):
                reject_clicked = True
                
        if approve_clicked:
            st.session_state.workflow_paused = False
            
            # Update the graph state to reflect the approval
            st.session_state.app_graph.update_state(
                st.session_state.thread_config,
                {"approval_status": "approved"}
            )
            
            async def resume_agent_approve():
                with st.spinner("Executing fix and writing post-mortem..."):
                    # Resume the graph
                    async for event in st.session_state.app_graph.astream(None, config=st.session_state.thread_config):
                        for node_name, state_update in event.items():
                            st.success(f"✅ Executed step: **{node_name}**")
                            
                            # Display the final post-mortem
                            if state_update and "messages" in state_update and len(state_update["messages"]) > 0:
                                report_content = state_update["messages"][-1].content
                                st.markdown(
                                    f'<div class="post-mortem-card">\n'
                                    f'<div class="post-mortem-header">📝 Official Post-Mortem Report</div>\n\n'
                                    f'{report_content}\n'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
            
            asyncio.run(resume_agent_approve())

        elif reject_clicked:
            st.session_state.workflow_paused = False
            
            # Update the graph state to reflect rejection
            st.session_state.app_graph.update_state(
                st.session_state.thread_config,
                {"approval_status": "rejected"}
            )
            
            async def resume_agent_reject():
                async for _ in st.session_state.app_graph.astream(None, config=st.session_state.thread_config):
                    pass
            
            asyncio.run(resume_agent_reject())
            st.error("Fix rejected. Agent workflow terminated.")
