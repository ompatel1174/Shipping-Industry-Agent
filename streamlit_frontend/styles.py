import streamlit as st

def inject_custom_css():
    """Injects custom CSS for a premium maritime look."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0ea5e9 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        font-size: 1rem;
        opacity: 0.85;
    }

    /* Sidebar styling refinements */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] h3 {
        color: #38bdf8 !important;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 1rem;
    }

    /* Sidebar divider */
    .sidebar-divider {
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 0.6rem 0;
    }

    /* Section label (Recent Chats, etc.) */
    .sidebar-section-label {
        color: #38bdf8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        font-weight: 600 !important;
        margin: 0.4rem 0 0.3rem 0 !important;
    }

    /* New Chat button – glowing accent */
    [data-testid="stSidebar"] div.stButton:first-child > button {
        background: linear-gradient(135deg, #0ea5e9, #2563eb);
        color: #fff !important;
        font-weight: 600;
        font-size: 0.92rem;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        box-shadow: 0 0 12px rgba(14,165,233,0.35);
        transition: box-shadow 0.25s, transform 0.15s;
    }
    [data-testid="stSidebar"] div.stButton:first-child > button:hover {
        box-shadow: 0 0 22px rgba(14,165,233,0.6);
        transform: translateY(-1px);
    }

    /* Example Queries toggle button */
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(56,189,248,0.3);
        color: #38bdf8 !important;
        font-weight: 600;
        border-radius: 8px;
        font-size: 0.85rem;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: rgba(56,189,248,0.12);
    }

    /* Recent chat item buttons */
    [data-testid="stSidebar"] div.stButton > button {
        padding: 0.28rem 0.75rem;
        font-size: 0.83rem;
        min-height: 0;
        border-radius: 8px;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background: rgba(255,255,255,0.04);
        border: 1px solid transparent;
        transition: background 0.18s, border-color 0.18s;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: rgba(14,165,233,0.12);
        border-color: rgba(14,165,233,0.35);
    }

    /* Chat message styling - more compact */
    [data-testid="stChatMessage"] {
        border-radius: 10px;
        padding: 0.5rem 0.7rem;
        margin-bottom: 0.4rem;
    }

    /* SQL expander */
    .sql-block {
        background: #1e293b;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 0.85rem;
        color: #e2e8f0;
        overflow-x: auto;
    }

    /* Tool badge */
    .tool-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 0.3rem;
    }
    .badge-vector { background: #1e40af; color: #93c5fd; }
    .badge-sql { background: #065f46; color: #6ee7b7; }
    .badge-calc { background: #92400e; color: #fcd34d; }

    /* Status indicators */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .dot-green { background: #22c55e; }
    .dot-blue { background: #3b82f6; }
    .dot-amber { background: #f59e0b; }
</style>
""", unsafe_allow_html=True)
