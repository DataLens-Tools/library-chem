"""
VOC-Insect-Plant Interaction Library
=====================================
A cheminformatics-enhanced library for Volatile Organic Compounds
and their interactions with insects, host plants, and natural enemies.

Run:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="VOC·BIO Library",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

/* Global */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Dark sidebar */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
}
[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem;
    padding: 4px 0;
}

/* Hero */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.4rem;
    color: #1a3a2a;
    line-height: 1.1;
    margin: 0;
}
.hero-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #4a7c59;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 8px;
}

/* Stat cards */
.stat-card {
    background: linear-gradient(135deg, #f0f9f4 0%, #e6f3ec 100%);
    border: 1px solid #b7dfc9;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.stat-number {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #1a3a2a;
    line-height: 1;
}
.stat-label {
    font-size: 0.78rem;
    color: #4a7c59;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Badges */
.badge-attractant {
    background: #d1fae5; color: #065f46;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
}
.badge-repellent {
    background: #fee2e2; color: #991b1b;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
}
.badge-class {
    background: #ede9fe; color: #4c1d95;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600;
}

/* Section headers */
.section-head {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #1a3a2a;
    border-bottom: 2px solid #b7dfc9;
    padding-bottom: 8px;
    margin-bottom: 20px;
}

/* Mol card */
.mol-card {
    background: white;
    border: 1px solid #d1fae5;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}

/* SMILES display */
.smiles-box {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    background: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 6px 10px;
    word-break: break-all;
    color: #24292f;
}

/* Info box */
.info-box {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.88rem;
    color: #166534;
    margin: 12px 0;
}

/* Footer */
.footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #8b949e;
    text-align: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #e6f3ec;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌿 VOC·BIO Library")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "Dashboard",
            "VOC Library",
            "Molecule Explorer",
            "Insect–Plant Database",
            "Bioassay Results",
            "Interaction Network",
            "Similarity Search",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#8b949e; line-height:1.6;'>
    Built with <b>Streamlit</b> + <b>RDKit</b><br>
    Cheminformatics-enhanced<br>
    insect–VOC–plant library<br><br>
    <i>Taif University ×<br>Collaboration Project</i>
    </div>
    """, unsafe_allow_html=True)


# ── Page Router ──────────────────────────────────────────────────────────────
if page == "Dashboard":
    from modules.dashboard import render
elif page == "VOC Library":
    from modules.voc_library import render
elif page == "Molecule Explorer":
    from modules.molecule_explorer import render
elif page == "Insect–Plant Database":
    from modules.insect_plant import render
elif page == "Bioassay Results":
    from modules.bioassay import render
elif page == "Interaction Network":
    from modules.network import render
elif page == "Similarity Search":
    from modules.similarity import render

render()
