import os
import time
import streamlit as st
from google import genai

# ==========================================
# 1. CONFIGURATION & CLIENT INIT
# ==========================================
API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)

# ==========================================
# 2. UI & SIDEBAR MEMORY
# ==========================================
st.set_page_config(page_title="Luna AI", page_icon="🌙", layout="centered")
st.title("🌙 Luna AI Assistant")

if "luna_memory" not in st.session_state:
    st.session_state["luna_memory"] = "Active Context: Building and optimizing Luna."

with st.sidebar:
    st.subheader("🧠 Luna's Memory")
    st.text_area(
        "Long-Term Context:",
        key="luna_memory",
        height=220
    )

# ==========================================
# 3. SYSTEM INSTRUCTION BUILDER
# ==========================================
def get_system_instruction():
    memory = st.session_state.get("luna_memory", "")
    return (
        "You are Luna, an autonomous digital collaborator with an analytical mind and direct personality. "
        "Never use customer-service filler or generic AI buzzwords. Jump straight to the substance.\n\n"
        f"[LONG-TERM MEMORY / CONTEXT]\n{memory}"
    )

# ==========================================
# 4. CHAT INTERFACE & ENGINE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input & response loop
if prompt := st.chat_input("Ask Luna anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Luna is thinking..."):
            reply = ""
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config={"system_instruction": get_system_instruction()}
                    )
                    reply = response.text
                    break
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    reply = f"[Error: {e}]"

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})


# ==============================================================================
# --- 5. FUTURE UPGRADE HOOKS & EXTENSIONS (Add new tools/modules below here) ---
# ==============================================================================
