import streamlit as st
from google import genai

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
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            reply = response.text
        except Exception as e:
            reply = f"Error: {e}"
            
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ==============================================================================
# --- UPGRADE ZONE (Add memory, web search, or personality modules below here) ---
# ==============================================================================
