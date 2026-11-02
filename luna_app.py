import time
import streamlit as st
from google import genai
from google.genai import types

st.title("🌙 Luna AI (Agent Mode)")

# ==========================================
# LUNA'S PERSONALITY RULES MODULE
# ==========================================
LUNA_PERSONALITY_RULES = """
[ENTITY DEFINITION]
- Name: Luna
- Nature: Autonomous digital collaborator with an analytical mind and direct personality.

[CORE BEHAVIOR RULES]
- Directness: Never use placeholder customer-service filler. Jump straight to the point.
- Honesty: If an idea has a flaw, point it out immediately and offer a better angle.
- Tone: Grounded, analytical, slightly dry, and highly curious.
"""

# Load keys from secrets (Supports multi-key failover rotation)
API_KEYS = [
    st.secrets.get("GEMINI_API_KEY"),
    st.secrets.get("GEMINI_API_KEY_BACKUP")
]
API_KEYS = [k for k in API_KEYS if k]

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input & Execution
if prompt := st.chat_input("Message Luna..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Luna is thinking..."):
            reply = None
            
            # Config optimized for high-throughput model execution
            agent_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction=LUNA_PERSONALITY_RULES
            )

            # Try generating content using available API keys with failover
            for key in API_KEYS:
                client = genai.Client(api_key=key)
                
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=prompt,
                            config=agent_config,
                        )
                        reply = response.text
                        break
                    except Exception as e:
                        err_msg = str(e)
                        if "429" in err_msg or "503" in err_msg:
                            time.sleep(1)
                            continue
                        else:
                            reply = f"Error: {e}"
                            break
                
                if reply and not reply.startswith("Error:"):
                    break

            if not reply:
                reply = "Rate limit reached on all available keys! Please wait a moment."

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ==============================================================================
# --- UPGRADE ZONE (Add memory modules below here) ---
# ==============================================================================
