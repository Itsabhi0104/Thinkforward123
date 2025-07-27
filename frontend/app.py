import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()  # loads GROQ_API_KEY if you need it in frontend (optional)

st.set_page_config(page_title="E‑commerce Chatbot", layout="wide")
st.title("E‑commerce Customer Support Chatbot")

if "session_id" not in st.session_state:
    user_id = st.text_input("Enter your user ID", value="1")
    if st.button("Start Chat Session"):
        resp = requests.post(
            "http://localhost:5000/sessions",
            json={"user_id": int(user_id)},
        )
        if resp.status_code == 201:
            st.session_state.session_id = resp.json()["session_id"]
            st.success(f"Session started: {st.session_state.session_id}")
        else:
            st.error("Failed to start session.")

if "session_id" in st.session_state:
    session_id = st.session_state.session_id
    query = st.text_input("Your question:")
    if st.button("Send"):
        resp = requests.post(
            "http://localhost:5000/chat",
            json={"session_id": session_id, "message": query},
        )
        if resp.status_code == 200:
            st.markdown(f"**AI:** {resp.json()['response']}")
        else:
            st.error("Error from backend.")

    if st.button("Refresh History"):
        resp = requests.get(f"http://localhost:5000/sessions/{session_id}/messages")
        if resp.status_code == 200:
            messages = resp.json()
            for m in messages:
                prefix = "👤 You:" if m["role"] == "user" else "🤖 AI:"
                st.markdown(f"{prefix} {m['content']}")
        else:
            st.error("Could not fetch history.")
