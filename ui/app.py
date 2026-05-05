import streamlit as st
import requests

st.set_page_config(page_title="Gemini SignalOps", page_icon="🚨")

st.title("🚨 Gemini SignalOps - SRE Command Center")

st.markdown("### Autonomous Incident Response")

# URL of the FastAPI backend
API_URL = "http://127.0.0.1:8000/incident"

service_name = st.text_input("Service Name", value="payment-service")
incident_msg = st.text_input("Incident Message", value="High Error Rate")

if st.button("Trigger Incident"):
    with st.spinner("Agent is analyzing logs, metrics, and deploy history..."):
        try:
            response = requests.post(API_URL, json={"service": service_name, "message": incident_msg})
            if response.status_code == 200:
                data = response.json()
                decision = data.get("decision", "No decision returned")
                st.success("Analysis Complete!")
                st.markdown("### Agent Decision")
                
                # Render the raw structured text nicely
                st.text(decision)
            else:
                st.error(f"Error from API: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")

if st.button("Apply Fix"):
    try:
        fix_url = API_URL.replace("/incident", "/fix")
        res = requests.post(fix_url)
        if res.status_code == 200:
            st.success(res.text)
        else:
            st.error("Failed to execute fix.")
    except Exception as e:
        st.error(f"Failed to connect: {e}")

