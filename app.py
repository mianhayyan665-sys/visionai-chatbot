import streamlit as st
from google import genai
from PIL import Image
import os
import time
from dotenv import load_dotenv

# Load secret environment variables from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

# Page UI & Enterprise Styling
st.set_page_config(
    page_title="VisionAI Enterprise", 
    page_icon="⚡", 
    layout="centered"
)

# High-Contrast & Clear Visibility CSS
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #f0f6fc !important; }
    .main-title { font-size: 2.3rem; font-weight: 800; text-align: center; color: #58a6ff !important; margin-bottom: 5px; }
    .sub-title { color: #8b949e !important; text-align: center; margin-bottom: 25px; font-size: 1rem; }
    
    .stChatMessage {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }
    
    .stChatMessage p, .stChatMessage span, .stChatMessage li, .stChatMessage div {
        color: #f0f6fc !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }

    .stChatMessage strong { color: #79c0ff !important; }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #1f242c !important;
        border-left: 4px solid #58a6ff !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #161b22 !important;
        border-left: 4px solid #238636 !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border: 2px solid #58a6ff !important;
        border-radius: 12px !important;
        padding: 4px !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #8b949e !important;
        font-size: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ VisionAI Enterprise</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multimodal Conversational Intelligence | English • اردو • Roman Urdu</div>', unsafe_allow_html=True)

# Validate API Key from .env
if not GEMINI_API_KEY:
    st.error("API Key nahi mili! Barah-e-karam .env file check karein.")
    st.stop()

# Google GenAI Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Sidebar: Image Upload & Controls
with st.sidebar:
    st.header("⚙️ Control Panel")
    uploaded_file = st.file_uploader("📷 Upload an Image to Analyze", type=["png", "jpg", "jpeg", "webp"])
    if uploaded_file:
        img_preview = Image.open(uploaded_file)
        st.image(img_preview, caption="Uploaded Image Preview", use_container_width=True)
    
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Assistant. You can ask me questions in English, Urdu, or Roman Urdu, or upload any image for instant analysis."}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input Box
if prompt := st.chat_input("Type your message or ask about the uploaded image..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_instruction = (
        "You are an advanced enterprise AI assistant built for high-level professional presentations.\n"
        "STRICT LINGUISTIC RULES:\n"
        "1. Strictly detect the user's input language and reply in the EXACT SAME language:\n"
        "   - If Roman Urdu, reply ONLY in fluent, natural Roman Urdu.\n"
        "   - If Urdu script, reply ONLY in proper Urdu script.\n"
        "   - If English, reply ONLY in professional English.\n"
        "2. Absolutely NEVER output Chinese characters, broken scripts, or gibberish.\n"
        "3. If an image is provided, extract all text accurately, describe diagrams/logos, and answer the question directly."
    )

    with st.chat_message("assistant"):
        with st.spinner("Processing with Vision AI..."):
            contents = []
            if uploaded_file is not None:
                uploaded_file.seek(0)
                contents.append(Image.open(uploaded_file))
            contents.append(prompt)

            bot_reply = None
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=contents,
                        config={"system_instruction": system_instruction}
                    )
                    bot_reply = response.text
                    break
                except Exception as err:
                    if "503" in str(err) or "UNAVAILABLE" in str(err):
                        time.sleep(2)
                        continue
                    else:
                        bot_reply = f"Error: {err}"
                        break
            
            if bot_reply is None:
                bot_reply = "Server par load tha, barah-e-karam dobara message karein."

            st.markdown(bot_reply)

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})