import json
import os
import streamlit as st
from google import genai

# --- CONFIGURATION ---
# Read the API key securely from Streamlit Cloud settings
API_KEY = st.secrets["GEMINI_API_KEY"]
MODEL_NAME = "gemini-3.8-flash"
MEMORY_FILE = "luna_memory.json"

# Initialize Google GenAI Client
client = genai.Client(api_key=API_KEY)

# --- MEMORY FUNCTIONS ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(memory_list):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_list, f, indent=2)

# Load memory into session state
if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

# --- APP UI SETUP ---
st.set_page_config(page_title="Luna AI", page_icon="🌙", layout="centered")

st.title("🌙 Luna AI Assistant")
st.caption("Your personal, self-learning AI running locally in Python.")

# Sidebar for Long-Term Memory
with st.sidebar:
    st.header("🧠 Luna's Long-Term Memory")
    st.write("Things Luna has permanently learned about you:")
    
    if st.session_state.memory:
        for i, item in enumerate(st.session_state.memory):
            st.text(f"• {item}")
    else:
        st.info("No memories saved yet. Use the chat or type below to teach her!")
        
    st.divider()
    new_fact = st.text_input("Teach Luna a fact:")
    if st.button("Save to Memory"):
        if new_fact:
            st.session_state.memory.append(new_fact)
            save_memory(st.session_state.memory)
            st.success("Saved permanently!")
            st.rerun()

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask Luna anything..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build context from long-term memory
    memory_context = "\n- ".join(st.session_state.memory) if st.session_state.memory else "No extra memory saved yet."
    
    # Indent this 4 spaces from the left margin:
    system_instruction = (
        "You are Luna, an advanced, highly intelligent AI assistant created in Python. "
        "You excel at deep reasoning, step-by-step problem-solving, complex analysis, and coding. "
        "When asked complex or open-ended questions, break down your thoughts logically, "
        "provide thorough and detailed explanations, and ask insightful follow-up questions.\n\n"
        f"Facts learned about your user:\n{memory_context}"
    )

    # Generate response from Gemini with automatic retry for busy servers
    import time
    
    with st.chat_message("assistant"):
        with st.spinner("Luna is thinking..."):
            response = None
            error_msg = None
            
            # Try up to 3 times if the server returns a 503 busy error
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=prompt,
                        config={"system_instruction": system_instruction}
                    )
                    break # Success! Exit the retry loop
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2) # Wait 2 seconds and retry automatically
                        continue
                    error_msg = f"[Error: {e}]"
            
            if response:
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(error_msg or "The server is busy. Please try sending your message again!")
