import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Set up page styling
st.set_page_config(page_title="Prem PBA", page_icon="🔍", layout="centered")

# Custom CSS to mimic Perplexity's minimal light-mode interface
st.markdown("""
    <style>
    .main {
        background-color: #FAFAFA;
    }
    .big-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 42px;
        font-weight: 600;
        text-align: center;
        color: #1F2937;
        margin-top: 10vh;
        margin-bottom: 25px;
        letter-spacing: -1px;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid #E5E7EB;
        background-color: #FFFFFF;
        color: #374151;
        font-size: 14px;
        padding: 6px 18px;
    }
    .stButton>button:hover {
        background-color: #F3F4F6;
        border-color: #D1D5DB;
    }
    </style>
""", unsafe_allow_html=True)

# Fetch API Key securely
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing! Configure it in Streamlit Secrets.")
    st.stop()

# Initialize session state for active prompt
if "input_query" not in st.session_state:
    st.session_state.input_query = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Top Header Title
st.markdown('<div class="big-title">Prem PBA</div>', unsafe_allow_html=True)

# --- SIDEBAR FOR EXTRA APPLICATIONS ---
with st.sidebar:
    st.title("⚡ Prem PBA Tools")
    st.success("🟢 Connected")
    
    # 1. Attachment / Image Analyzer
    st.subheader("📎 Attach Files & Images")
    uploaded_file = st.file_uploader("Upload image for analysis:", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Attached Image", use_container_width=True)
        
    # 2. Mode Selector
    st.divider()
    search_mode = st.selectbox(
        "Focus Mode:",
        ["All / Web Search", "Code Assistant", "Deep Academic Research", "Creative Writing"]
    )
    
    # 3. Clear Chat
    if st.button("🗑️ Clear Workspace", use_container_width=True):
        st.session_state.messages = []
        st.session_state.input_query = ""
        st.rerun()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick action suggestion chip handler
def set_query(query_text):
    st.session_state.input_query = query_text

# Action Chips (Mimicking screenshot layout)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📝 Summarise"):
        set_query("Summarise the key points of: ")
with col2:
    if st.button("🔍 Research"):
        set_query("Provide a detailed research analysis on: ")
with col3:
    if st.button("⭐ Recommend"):
        set_query("Give me top recommendations for: ")
with col4:
    if st.button("✈️ Travel"):
        set_query("Create a travel itinerary for: ")

st.write("")

# Chat Input Area
prompt = st.chat_input("Ask anything...", key="chat_input")

# Use button selection if chat input is empty
final_prompt = prompt or st.session_state.input_query

if final_prompt and (prompt or st.session_state.input_query):
    # Reset preset query
    st.session_state.input_query = ""
    
    # Display user query
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching & Reasoning..."):
            try:
                prompt_parts = [{"text": f"System Mode: {search_mode}\nUser Request: {final_prompt}"}]
                
                # Image processing if attached
                if uploaded_file:
                    image_bytes = uploaded_file.getvalue()
                    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                    prompt_parts.append({
                        "inline_data": {
                            "mime_type": uploaded_file.type,
                            "data": encoded_image
                        }
                    })

                # API call using stable endpoint
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
                    st.error(f"Error: {result.get('error', {}).get('message', 'API Request failed')}")

            except Exception as e:
                st.error(f"Execution Error: {e}")
