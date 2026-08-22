import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Complete GenAI Chatbot", page_icon="🤖", layout="wide")
st.title("Complete GenAI Assistant 🤖")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ App Settings")

# 1. API Key Handling
env_api_key = os.getenv("GEMINI_API_KEY")
if env_api_key:
    api_key = env_api_key
    st.sidebar.success("API Key loaded automatically!")
else:
    api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

# 2. AI Persona Selection
persona = st.sidebar.selectbox(
    "Choose AI Persona:",
    ["Default Assistant", "Senior Python Engineer", "Poet", "5-Year-Old Translator"]
)

# 3. Creativity Slider
temperature = st.sidebar.slider(
    "Creativity (Temperature):",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1
)

# 4. Image Uploader (Multimodal Support)
uploaded_image = st.sidebar.file_uploader("Upload an Image (Optional):", type=["png", "jpg", "jpeg"])

# 5. Clear Chat Button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# --- SYSTEM PROMPTS MAP ---
system_prompts = {
    "Default Assistant": "You are a helpful, accurate, and concise AI assistant.",
    "Senior Python Engineer": "You are an expert Python developer. Provide clean, well-commented code examples.",
    "Poet": "You respond to all prompts in creative, expressive rhyming verse.",
    "5-Year-Old Translator": "Explain everything in simple, easy terms as if speaking to a 5-year-old child."
}

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT & API CALL ---
if user_prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error("Please provide a valid Gemini API Key in your .env or sidebar!")
        st.stop()

    # Display user's message immediately
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Prepare message payload
    user_parts = [{"text": user_prompt}]

    # Process image if uploaded
    if uploaded_image:
        bytes_data = uploaded_image.getvalue()
        base64_image = base64.b64encode(bytes_data).decode("utf-8")
        user_parts.append({
            "inline_data": {
                "mime_type": uploaded_image.type,
                "data": base64_image
            }
        })
        st.sidebar.image(uploaded_image, caption="Attached Image", use_column_width=True)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Structure API request with persona, temperature, and full context
    payload = {
        "system_instruction": {
            "parts": [{"text": system_prompts[persona]}]
        },
        "contents": [{
            "parts": user_parts
        }],
        "generationConfig": {
            "temperature": temperature
        }
    }

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
                st.markdown(ai_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_text})
            else:
                st.error(f"Error {response.status_code}: {response.text}")