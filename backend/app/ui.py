import os
from uuid import uuid4

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Privacy-Preserved Wellbeing Intelligence Engine",
    page_icon=":seedling:",
    layout="wide",
)
st.title("Privacy-Preserved Wellbeing Intelligence Engine")
st.caption("Supportive conversation and local retrieval. This is not a diagnostic system.")

if "user_id" not in st.session_state:
    st.session_state.user_id = f"local-{uuid4().hex[:12]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loaded_user" not in st.session_state:
    st.session_state.loaded_user = ""
if "last_risk" not in st.session_state:
    st.session_state.last_risk = "NOT ASSESSED"
if "last_grounding" not in st.session_state:
    st.session_state.last_grounding = {"status": "unavailable", "sources": []}

with st.sidebar:
    st.header("Session")
    user_id = st.text_input("Local user ID", key="user_id", max_chars=128).strip()
    risk_colors = {"LOW": "#24804d", "CONCERNING": "#ac7620", "HIGH": "#b4463f"}
    risk_color = risk_colors.get(st.session_state.last_risk, "#69756f")
    st.markdown(
        f'<span style="color:{risk_color};font-weight:700">● {st.session_state.last_risk}</span>',
        unsafe_allow_html=True,
    )
    st.caption("A keyword intercept and unvalidated sentiment proxy; not a clinical risk score.")

    if st.button("Clear this session", use_container_width=True, disabled=not user_id):
        try:
            result = requests.delete(
                f"{API_BASE_URL}/api/chat/history/{user_id}", timeout=(3, 10)
            )
            result.raise_for_status()
            st.session_state.messages = []
            st.session_state.last_risk = "NOT ASSESSED"
            st.session_state.last_grounding = {"status": "unavailable", "sources": []}
            st.session_state.loaded_user = user_id
            st.rerun()
        except requests.RequestException:
            st.error("Could not clear the session. Check that the local API is running.")

    st.divider()
    st.caption("Messages and retrieved excerpts are sent to OpenAI only when an API key is configured. Session history is stored locally in SQLite.")

if not user_id:
    st.info("Enter a local user ID in the sidebar to open a session.")
    st.stop()

if st.session_state.loaded_user != user_id:
    try:
        result = requests.get(
            f"{API_BASE_URL}/api/chat/history/{user_id}", timeout=(3, 10)
        )
        result.raise_for_status()
        history = result.json().get("messages", [])
        st.session_state.messages = [
            {"role": item["role"], "content": item["content"]}
            for item in history
            if item.get("role") in {"user", "assistant"}
        ]
        st.session_state.loaded_user = user_id
    except requests.RequestException:
        st.session_state.messages = []
        st.session_state.loaded_user = user_id
        st.warning("The local API is unavailable. Start the project services and retry.")

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

prompt = st.chat_input("Share what is on your mind")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        with st.chat_message("assistant"):
            with st.spinner("Preparing a supportive response..."):
                result = requests.post(
                    f"{API_BASE_URL}/api/chat",
                    json={"user_id": user_id, "message": prompt},
                    timeout=(3, 60),
                )
                result.raise_for_status()
                payload = result.json()
                st.markdown(payload["response"])
        st.session_state.messages.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": payload["response"]},
            ]
        )
        st.session_state.last_risk = payload["risk_assessment"]["risk_level"]
        st.session_state.last_grounding = payload["grounding"]
        st.rerun()
    except requests.Timeout:
        st.error("The response service took too long. Your message was not confirmed; please check history before retrying.")
    except requests.RequestException:
        st.error("The local API is unavailable or rejected the request. Your message was not confirmed.")

with st.expander("Grounding & Safety Provenance"):
    st.write(f"Grounding status: {st.session_state.last_grounding.get('status', 'unavailable')}")
    st.write(f"Safety signal: {st.session_state.last_risk}")
    sources = st.session_state.last_grounding.get("sources", [])
    if sources:
        st.dataframe(sources, use_container_width=True, hide_index=True)
    else:
        st.caption("No retrieval source metadata is available for the current response.")