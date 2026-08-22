import os
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load local environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(page_title="GenAI Assistant", page_icon="🤖")
st.title("🤖 GenAI Assistant")

# Fetch API key automatically from Streamlit Cloud Secrets or local .env file
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Gemini API Key not found! Please check your Streamlit Secrets or .env file.")
    st.stop()

# Initialize chat memory in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask me anything..."):
    # Display user query in chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send request to Gemini API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = requests.post(url, headers=headers, json=data)
                result = response.json()

                if response.status_code == 200:
                    bot_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    error_msg = result.get("error", {}).get("message", "Failed to connect to API.")
                    st.error(f"API Error: {error_msg}")

            except Exception as e:
                st.error(f"An error occurred: {e}")
