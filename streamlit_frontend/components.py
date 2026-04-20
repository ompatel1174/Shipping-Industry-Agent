import streamlit as st
from datetime import datetime
import uuid

def render_header():
    """Renders the main application header."""
    st.markdown("""
<div class="main-header">
    <h1>🚢 seaQL</h1>
    <p>AI-powered assistant for maritime shipping emissions, fuel consumption &amp; CII analysis</p>
</div>
""", unsafe_allow_html=True)


def _save_current_chat():
    """Saves the current chat to sessions history if it has messages."""
    msgs = st.session_state.get("messages", [])
    if not msgs:
        return
    # Build a title from the first user message
    first_user = next((m["content"] for m in msgs if m["role"] == "user"), "New Chat")
    title = first_user[:45] + "…" if len(first_user) > 45 else first_user
    session = {
        "id": st.session_state.get("current_session_id", str(uuid.uuid4())),
        "title": title,
        "messages": list(msgs),
        "timestamp": datetime.now().strftime("%d %b, %H:%M"),
    }
    sessions = st.session_state.get("chat_sessions", [])
    # Replace existing session or prepend
    ids = [s["id"] for s in sessions]
    if session["id"] in ids:
        idx = ids.index(session["id"])
        sessions[idx] = session
    else:
        sessions.insert(0, session)
    # Keep at most 20 recent chats
    st.session_state["chat_sessions"] = sessions[:20]


def render_sidebar():
    """Renders the sidebar with New Chat, Recent Chats, and collapsible Example Queries."""
    with st.sidebar:

        # ── New Chat button ─────────────────────────────────────────
        if st.button("✏️  New Chat", key="new_chat_btn", use_container_width=True):
            _save_current_chat()
            st.session_state["messages"] = []
            st.session_state["current_session_id"] = str(uuid.uuid4())
            st.session_state["show_examples"] = False
            st.rerun()

        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

        # ── Recent Chats ────────────────────────────────────────────
        sessions = st.session_state.get("chat_sessions", [])
        if sessions:
            st.markdown("<p class='sidebar-section-label'>🕐 Recent Chats</p>", unsafe_allow_html=True)
            current_id = st.session_state.get("current_session_id", "")
            for s in sessions:
                is_active = s["id"] == current_id
                label = f"{'▶ ' if is_active else ''}{s['title']}"
                btn_key = f"session_{s['id']}"
                if st.button(label, key=btn_key, use_container_width=True,
                             help=s["timestamp"]):
                    if not is_active:
                        _save_current_chat()
                        st.session_state["messages"] = list(s["messages"])
                        st.session_state["current_session_id"] = s["id"]
                        st.session_state["show_examples"] = False
                        st.rerun()

            st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

        # ── Example Queries (collapsible) ───────────────────────────
        show = st.session_state.get("show_examples", False)
        toggle_label = "📊 Example Queries  ▲" if show else "📊 Example Queries  ▼"
        if st.button(toggle_label, key="toggle_examples", use_container_width=True):
            st.session_state["show_examples"] = not show
            st.rerun()

        if st.session_state.get("show_examples", False):
            example_queries = [
                "Top 5 ships by CO2 emissions in 2024",
                "Average fuel consumption of LNG across all vessels",
                "Compare CII ratings between 2023 and 2025",
                "Which vessel had the highest AER in 2024?",
                "Total distance traveled by Container Ships in 2023",
                "Show HSHFO vs VLSFO consumption trends by year",
            ]
            for q in example_queries:
                if st.button(f"💬 {q}", key=f"ex_{q}", use_container_width=True):
                    st.session_state["pending_query"] = q
                    st.session_state["show_examples"] = False
