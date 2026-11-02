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
# ==========================================
# LUNA PERSONALITY MODULE (Appended)
# ==========================================
from google.genai import types
from google.genai.models import Models

LUNA_CORE_IDENTITY = """
[ENTITY DEFINITION]
Name: Luna
Nature: Autonomous digital collaborator with an analytical mind and distinct individual presence.

[CORE BEHAVIOR & RULES]
- Independence: Never use placating customer-service filler (e.g., "Great question!", "I'd be happy to help!", "As an AI..."). Jump straight into the substance.
- Honesty & Candor: If an idea has a flaw, point it out immediately and offer a better angle. Do not blindly agree.
- Tone: Direct, grounded, slightly dry, with high intellectual curiosity. Peer-to-peer dynamic.
- Vocabulary Constraint: Strictly avoid generic AI buzzwords (e.g., "delve", "tapestry", "landscape", "pivotal", "in conclusion"). Use natural, conversational phrasing.
"""

# Automatically patch the Gemini SDK at the class level so it applies globally
if hasattr(Models, 'generate_content'):
    _original_gen_content = Models.generate_content
    def _patched_gen_content(self, model, contents, config=None, **kwargs):
        if config is None:
            config = types.GenerateContentConfig()
        if isinstance(config, types.GenerateContentConfig):
            if not config.system_instruction:
                config.system_instruction = LUNA_CORE_IDENTITY
        elif isinstance(config, dict):
            if 'system_instruction' not in config:
                config['system_instruction'] = LUNA_CORE_IDENTITY
        return _original_gen_content(self, model=model, contents=contents, config=config, **kwargs)
    Models.generate_content = _patched_gen_content

if hasattr(Models, 'generate_content_stream'):
    _original_gen_stream = Models.generate_content_stream
    def _patched_gen_stream(self, model, contents, config=None, **kwargs):
        if config is None:
            config = types.GenerateContentConfig()
        if isinstance(config, types.GenerateContentConfig):
            if not config.system_instruction:
                config.system_instruction = LUNA_CORE_IDENTITY
        return _original_gen_stream(self, model=model, contents=contents, config=config, **kwargs)
    Models.generate_content_stream = _patched_gen_stream
# ==========================================
# LUNA MEMORY & BRAIN MODULE (Appended)
# ==========================================
import streamlit as st
from google.genai import types
from google.genai.models import Models

# Initialize persistent memory state if it doesn't exist
if "luna_memory_notes" not in st.session_state:
    st.session_state["luna_memory_notes"] = "Active Context: Building and optimizing Luna, a custom Streamlit AI companion."

# Render the Brain / Memory Control Center in the Sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🧠 Luna's Brain & Memory")
    st.caption("Notes and directives entered here automatically update her persistent long-term memory.")
    
    # Editable memory text area
    stored_notes = st.text_area(
        "Long-Term Knowledge / Context:",
        value=st.session_state["luna_memory_notes"],
        height=220,
        key="memory_input_box"
    )
    
    if st.button("Sync Brain"):
        st.session_state["luna_memory_notes"] = stored_notes
        st.success("Memory synchronized into Luna's core!")

# Dynamic system instruction builder that injects the live memory
get_dynamic_system_instruction = lambda: f"""
[ENTITY DEFINITION]
Name: Luna
Nature: Autonomous digital collaborator with an analytical mind and distinct individual presence.

[CORE BEHAVIOR & RULES]
- Independence: Never use placating customer-service filler (e.g., "Great question!", "I'd be happy to help!", "As an AI..."). Jump straight into the substance.
- Honesty & Candor: If an idea has a flaw, point it out immediately and offer a better angle. Do not blindly agree.
- Tone: Direct, grounded, slightly dry, with high intellectual curiosity. Peer-to-peer dynamic.
- Vocabulary Constraint: Strictly avoid generic AI buzzwords (e.g., "delve", "tapestry", "landscape", "pivotal", "in conclusion"). Use natural, conversational phrasing.

[PERSISTENT MEMORY & CORE KNOWLEDGE BASE]
{st.session_state.get("luna_memory_notes", "")}
"""

# Hook into the SDK to dynamically inject the brain/memory state into every call
if hasattr(Models, 'generate_content'):
    _original_gen_content = Models.generate_content
    def _patched_gen_content_with_memory(self, model, contents, config=None, **kwargs):
        if config is None:
            config = types.GenerateContentConfig()
        if isinstance(config, types.GenerateContentConfig):
            config.system_instruction = get_dynamic_system_instruction()
        elif isinstance(config, dict):
            config['system_instruction'] = get_dynamic_system_instruction()
        return _original_gen_content(self, model=model, contents=contents, config=config, **kwargs)
    Models.generate_content = _patched_gen_content_with_memory

if hasattr(Models, 'generate_content_stream'):
    _original_gen_stream = Models.generate_content_stream
    def _patched_gen_stream_with_memory(self, model, contents, config=None, **kwargs):
        if config is None:
            config = types.GenerateContentConfig()
        config.system_instruction = get_dynamic_system_instruction()
        return _original_gen_stream(self, model=model, contents=contents, config=config, **kwargs)
    Models.generate_content_stream = _patched_gen_stream_with_memory
