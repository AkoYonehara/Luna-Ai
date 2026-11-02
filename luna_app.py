import os
import json
import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai.models import Models

# ==========================================
# 1. CONFIGURATION & CLIENT INITIALIZATION
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]
SPEED_MODEL = "gemini-2.5-flash"
MEMORY_FILE = "luna_memory.json"

client = genai.Client(api_key=API_KEY)


# ==========================================
# 2. MEMORY & BRAIN MODULE
# ==========================================
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
# 3. SELF-INSPECTION MODULE
# ==========================================
try:
    with open("luna_app.py", "r", encoding="utf-8") as f:
        raw_code = f.read()[:3000]
        SOURCE_CODE_SNAPSHOT = raw_code.replace("{", "{{").replace("}", "}}")
except Exception:
    SOURCE_CODE_SNAPSHOT = "Source code unavailable."


# ==========================================
# 4. DYNAMIC SYSTEM INSTRUCTION BUILDER
# ==========================================
def get_unified_system_instruction():
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
# 5. SDK MONKEY-PATCH MODULE (Speed, Web Search, Persona)
# ==========================================
search_tool = types.Tool(google_search=types.GoogleSearch())

# Secure the TRUE original methods permanently on first boot to prevent recursion loops
if not hasattr(Models, '_true_generate_content'):
    Models._true_generate_content = Models.generate_content

if not hasattr(Models, '_true_generate_content_stream'):
    Models._true_generate_content_stream = Models.generate_content_stream

def _patched_gc_unified(self, model, contents, config=None, **kwargs):
    if not model or "pro" in str(model) or model == "gemini-3.8-flash":
        model = SPEED_MODEL
    if config is None:
        config = types.GenerateContentConfig()
        
    if isinstance(config, types.GenerateContentConfig):
        config.system_instruction = get_unified_system_instruction()
        existing_tools = config.tools or []
        if search_tool not in existing_tools:
            config.tools = existing_tools + [search_tool]
    elif isinstance(config, dict):
        config['system_instruction'] = get_unified_system_instruction()
        tools = config.get('tools', [])
        if search_tool not in tools:
            config['tools'] = tools + [search_tool]
            
    return Models._true_generate_content(self, model=model, contents=contents, config=config, **kwargs)

def _patched_gcs_unified(self, model, contents, config=None, **kwargs):
    if not model or "pro" in str(model) or model == "gemini-3.8-flash":
        model = SPEED_MODEL
    if config is None:
        config = types.GenerateContentConfig()
        
    if isinstance(config, types.GenerateContentConfig):
        config.system_instruction = get_unified_system_instruction()
        existing_tools = config.tools or []
        if search_tool not in existing_tools:
            config.tools = existing_tools + [search_tool]
    elif isinstance(config, dict):
        config['system_instruction'] = get_unified_system_instruction()
        tools = config.get('tools', [])
        if search_tool not in tools:
            config['tools'] = tools + [search_tool]
            
    return Models._true_generate_content_stream(self, model=model, contents=contents, config=config, **kwargs)

Models.generate_content = _patched_gc_unified
Models.generate_content_stream = _patched_gcs_unified


# ==========================================
# 6. APP UI & CHAT INTERFACE
# ==========================================
st.set_page_config(page_title="Luna AI", page_icon="🌙", layout="centered")

st.title("🌙 Luna AI Assistant")
st.caption("Autonomous digital collaborator powered by Gemini.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user chat input
if prompt := st.chat_input("Ask Luna anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Luna is thinking..."):
            response = None
            error_msg = None
            
            # Retry loop for resilience against server busy errors
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=SPEED_MODEL,
                        contents=prompt
                    )
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
