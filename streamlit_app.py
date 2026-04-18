import streamlit as st
import pandas as pd
import json
import requests
import os
import sys

# Add the parent directory to sys.path to allow importing the 'app' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from streamlit_frontend.styles import inject_custom_css
from streamlit_frontend.components import render_header, render_sidebar

# ───────────────────────── Page Config ───────────────────────────
st.set_page_config(
    page_title="FuelAgent – Shipping Emissions Assistant",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────── Initialize Session State ────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "current_session_id" not in st.session_state:
    import uuid
    st.session_state.current_session_id = str(uuid.uuid4())
if "show_examples" not in st.session_state:
    st.session_state.show_examples = False

# ───────────────────────── Logic Functions ─────────────────────────

def get_stream_generator(query, history, metadata_ref):
    """Creates a generator that calls the backend and updates metadata."""
    try:
        with requests.post(
            settings.API_URL,
            json={"query": query, "chat_history": history},
            stream=True,
            timeout=60
        ) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        part = json.loads(line.decode("utf-8"))
                        if "sql" in part:
                            metadata_ref["sql"] = part["sql"]
                        elif "data" in part:
                            metadata_ref["data"] = part["data"]
                            metadata_ref["columns"] = part["columns"]
                        elif "chunk" in part:
                            yield part["chunk"]
                        elif "error" in part:
                            metadata_ref["error"] = part["error"]
            else:
                yield f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        yield f"Connection Error: {str(e)}"

def render_metadata_expanders(metadata):
    """Renders SQL and Data expanders."""
    if metadata.get("sql"):
        with st.expander("🔍 View SQL Query", expanded=False):
            st.code(metadata["sql"], language="sql")

    if metadata.get("data") is not None and len(metadata["data"]) > 0:
        with st.expander(f"📋 View Data ({len(metadata['data'])} rows)", expanded=False):
            df = pd.DataFrame(metadata["data"])
            st.dataframe(df, use_container_width=True)

            # Auto-chart
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if len(numeric_cols) >= 1 and len(df) <= 50:
                non_numeric = [c for c in df.columns if c not in numeric_cols]
                if non_numeric:
                    chart_df = df.set_index(non_numeric[0])[numeric_cols[:3]]
                    st.bar_chart(chart_df)

# ───────────────────────── Render UI ──────────────────────────────
inject_custom_css()
render_header()
render_sidebar()
#st.sidebar.markdown(f"**API Status**: Connecting to {settings.API_URL}")

# ───────────────────────── Chat Interface ──────────────────────────

# Render History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🚢"):
        st.markdown(msg["content"])
        render_metadata_expanders(msg)

# Handle Input
pending = st.session_state.pop("pending_query", None)
user_input = st.chat_input("Ask me about shipping emissions, fuel data, or CII ratings...")
query = pending or user_input

if query:
    # Auto-save current chat to sidebar history on every new message
    from streamlit_frontend.components import _save_current_chat
    _save_current_chat()

    # Display user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(query)
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Process with FastAPI backend
    with st.chat_message("assistant", avatar="🚢"):
        metadata = {"sql": None, "data": None, "columns": None, "error": None}
        
        # Prepare history
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ][-10:]
        
        # Use the streaming generator
        stream = get_stream_generator(query, history, metadata)
        full_response = st.write_stream(stream)

        # Post-stream UI updates
        render_metadata_expanders(metadata)

        if metadata["error"]:
            st.error(f"⚠️ {metadata['error']}")
            
        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "sql": metadata["sql"],
            "data": metadata["data"],
        })
