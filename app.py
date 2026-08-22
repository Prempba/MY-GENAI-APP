import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="GenAI Assistant", page_icon="🤖", layout="wide")

# Fetch API Key securely from Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing from Secrets.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ App Settings")
    st.success("API Key loaded successfully!")
    
    system_persona = st.selectbox(
        "Choose Assistant Persona:",
        ["Helpful Assistant", "Code Expert", "Creative Writer", "Strict Tutor"]
    )
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 GenAI Assistant")
st.caption(f"Currently acting as: **{system_persona}**")

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Add persona context to prompt
                full_prompt = f"System Persona: Act as a {system_persona}.\nUser Query: {prompt}"
                
              url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {"contents": [{"parts": [{"text": full_prompt}]}]}
                
                response = requests.post(url, headers=headers, json=data)
                result = response.json()

                if response.status_code == 200:
                    bot_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    st.error(f"Error: {result.get('error', {}).get('message', 'API request failed')}")

            except Exception as e:
                st.error(f"Error: {e}")
