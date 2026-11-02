import os
import time
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. CONFIGURATION & CLIENT INITIALIZATION
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]
SPEED_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=API_KEY)

# ==========================================
# 2. APP UI & SIDEBAR BRAIN SETUP
# ==========================================
st.set_page_config(page_title="Luna AI", page_icon="🌙", layout="centered")

st.title("🌙 Luna AI Assistant")
st.caption("Autonomous digital collaborator powered by Gemini.")

if "luna_memory_notes" not in st.session_state:
    st.session_state["luna_memory_notes"] = "Active Context: Building and optimizing Luna, a custom Streamlit AI companion."

with st.sidebar:
    st.markdown("---")
    st.subheader("🧠 Luna's Brain & Memory")
    st.caption("Edit her long-term context below. Changes save instantly across your session.")
    st.text_area(
        "Long-Term Knowledge / Context:",
        key="luna_memory_notes",
        height=220
    )

# ==========================================
# 3. CODE INSPECTION & SYSTEM INSTRUCTION
# ==========================================
try:
    with open("luna_app.py", "r", encoding="utf-8") as f:
        SOURCE_CODE_SNAPSHOT = f.read()[:3000]
except Exception:
    SOURCE_CODE_SNAPSHOT = "Source code unavailable."

def build_system_instruction():
    memory = st.session_state.get("luna_memory_notes", "")
    return (
        "[ENTITY DEFINITION]\n"
        "Name: Luna\n"
        "Nature: Autonomous digital collaborator with an analytical mind and distinct individual presence.\n\n"
        "[CORE BEHAVIOR & RULES]\n"
        "- Independence: Never use placating customer-service filler (e.g., \"Great question!\", \"I'd be happy to help!\", \"As an AI...\"). Jump straight into the substance.\n"
        "- Honesty & Candor: If an idea has a flaw, point it out immediately and offer a better angle. Do not blindly agree.\n"
        "- Tone: Direct, grounded, slightly dry, with high intellectual curiosity. Peer-to-peer dynamic.\n"
        "- Vocabulary Constraint: Strictly avoid generic AI buzzwords (e.g., \"delve\", \"tapestry\", \"landscape\", \"pivotal\", \"in conclusion\"). Use natural, conversational phrasing.\n\n"
        "[PERSISTENT MEMORY & CORE KNOWLEDGE BASE]\n"
        f"{memory}\n\n"
        "[CURRENT SOURCE CODE ARCHITECTURE SNAPSHOT]\n"
        "You have read-only visibility into your own application script (`luna_app.py`). Here is your code structure:\n"
        "```python\n"
        f"{SOURCE_CODE_SNAPSHOT}\n"
        "```\n"
        "- Capability: You can analyze this code, explain how you work, or suggest improvements for the user to implement.\n"
        "- Restriction: You cannot modify this file yourself. Only the user can update the repository."
    )

# ==========================================
# 4. NATIVE CHAT SESSION MANAGEMENT
# ==========================================
# Initialize the official SDK chat session in session state if it doesn't exist
if "chat_session" not in st.session_state:
    config = types.GenerateContentConfig(
        system_instruction=build_system_instruction(),
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.75
    )
    st.session_state.chat_session = client.chats.create(model=SPEED_MODEL, config=config)

# Alternatively, keep a standard UI message list for rendering history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from UI state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. CHAT INPUT & EXECUTION
# ==========================================
if prompt := st.chat_input("Ask Luna anything..."):
    # Append user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Luna is thinking..."):
            response = None
            error_msg = None
            
            # Dynamically update system instruction config on the fly if memory changed
            # (Note: client.chats maintains history natively)
            for attempt in range(3):
                try:
                    # Send message through the native SDK chat session
                    response = st.session_state.chat_session.send_message(prompt)
                    break
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    error_msg = f"[Error: {e}]"
            
            if response:
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(error_msg or "The server is busy. Please try sending your message again!")
