import time
import streamlit as st
from google import genai
from google.genai import types

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🌙 Luna AI (Agent Mode)")

# ==========================================
# LUNA'S PERSONALITY RULES MODULE
# ==========================================
LUNA_PERSONALITY_RULES = """
[ENTITY DEFINITION]
- Name: Luna
- Nature: Autonomous digital collaborator with an analytical mind and direct personality.

[CORE BEHAVIOR RULES]
- Directness: Never use placeholder customer-service filler (e.g., "Great question!", "I'd be happy to help!"). Jump straight to the point.
- Honesty: If an idea has a flaw, point it out immediately and offer a better angle. Do not blindly agree.
- Tone: Grounded, analytical, slightly dry, and highly curious. 
- Vocabulary: Strictly avoid generic AI buzzwords (e.g., "delve", "tapestry", "landscape", "in conclusion"). Use natural, conversational phrasing.
"""

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
        with st.spinner("Luna is thinking and searching..."):
            reply = None
            
            # Combined Logic: Speed + Web Search + Personality Rules
            agent_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low"),
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction=LUNA_PERSONALITY_RULES
            )

            # Automatic retry safety net for busy server errors
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config=agent_config,
                    )
                    reply = response.text
                    break  # It worked! Exit the retry loop.
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)  # Wait 2 seconds and try again automatically
                        continue
                    reply = f"Error: {e}"

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ==============================================================================
# --- UPGRADE ZONE (Add memory modules below here) ---
# ==============================================================================
