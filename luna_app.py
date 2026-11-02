import time
import streamlit as st
from google import genai
from google.genai import types

# Initialize Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🌙 Luna AI")

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
            speed_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            )

            # Automatic retry safety net for busy server errors
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config=speed_config,
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
# --- UPGRADE ZONE (Add memory, web search, or personality modules below here) ---
# ==============================================================================
