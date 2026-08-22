import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load environment variables for local testing
load_dotenv()

st.set_page_config(page_title="GenAI Multi-Modal Suite", page_icon="🤖", layout="wide")

# Securely retrieve API Key from Secrets or Local .env
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Set it in Streamlit Secrets.")
    st.stop()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.success("🟢 API Key Loaded")
    
    # 1. Persona Switcher
    system_persona = st.selectbox(
        "Choose Assistant Persona:",
        ["Helpful Assistant", "Code Expert", "Creative Writer", "Data Analyst"]
    )
    
    # 2. Image Uploader Feature
    st.subheader("📷 Vision Analysis")
    uploaded_image = st.file_uploader("Upload an image to ask questions about it:", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image Preview", use_container_width=True)
    
    # 3. Clear Chat Button
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 GenAI Multi-Modal Suite")
st.caption(f"Active Mode: **{system_persona}**")

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if prompt := st.chat_input("Ask a question or describe your image..."):
    # Render user prompt in chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Prepare API payload parts
                prompt_parts = [{"text": f"System Persona: Act as a {system_persona}.\nUser Query: {prompt}"}]
                
                # Convert image to base64 if uploaded
                if uploaded_image:
                    image_bytes = uploaded_image.getvalue()
                    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                    prompt_parts.append({
                        "inline_data": {
                            "mime_type": uploaded_image.type,
                            "data": encoded_image
                        }
                    })

                # API Request to Gemini
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {"contents": [{"parts": prompt_parts}]}

                response = requests.post(url, headers=headers, json=payload)
                result = response.json()

                if response.status_code == 200:
                    bot_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    err_details = result.get("error", {}).get("message", "API Request Failed")
                    st.error(f"Error: {err_details}")

            except Exception as e:
                st.error(f"Execution Error: {e}")
