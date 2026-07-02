import logging
import os
import streamlit as st

# Assuming these exist in your core directory
from core.prompts import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, THEMES,
)
from core.engine import (
    get_gemini_client, run_research_pass, run_extraction_pass, run_enhancement_pass,
)
from core.doc_maker import (
    generate_docx_bytes, generate_markdown, generate_ats_text,
)

# --- CONFIGURATION & MAPPING ---
STREAM_DATA = {
    "BSc": {
        "roles": ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", "Cloud Architect"],
        "description": "BSc Computer Science/Tech"
    },
    "BBA": {
        "roles": ["Marketing Manager", "Business Analyst", "Operations Manager", "HR Specialist"],
        "description": "BBA Management/Business"
    },
    "MBA": {
        "roles": ["Management Consultant", "Product Manager", "Financial Strategist", "Business Development Manager"],
        "description": "MBA Professional/Leadership"
    }
}

# --- LOGGING & PAGE CONFIG ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] — %(message)s")
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# ... [Keep your existing CSS block here] ...

# --- HEADER ---
st.markdown(f"""
<div class="hero-container">
  <div class="hero-overlay">
    <div class="hero-title">Design Your <span>Future Resume</span></div>
    <p class="hero-sub">Select your stream and dream roles. We will architect your 3-year career path, including the free certifications you need to get there.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("## ⚙️ Configuration")
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
theme = st.sidebar.selectbox("🎨 Output Theme", options=THEMES, index=1)

# --- DYNAMIC INPUT AREA ---
st.markdown("### 🎓 Step 1: Select Your Stream")
selected_stream = st.selectbox("Choose your degree program:", options=list(STREAM_DATA.keys()))

st.markdown("### 🎯 Step 2: Select Career Goals")
available_roles = STREAM_DATA[selected_stream]["roles"]
selected_roles = st.multiselect(
    f"What are your target roles as a {selected_stream} student? (Max 3)",
    options=available_roles,
    max_selections=3
)

build_clicked = st.button("🚀 Generate My Future Resume")

# --- PIPELINE ---
if build_clicked:
    if not selected_roles or not api_key:
        st.warning("⚠️ Please provide your API Key and select at least one role.")
        st.stop()

    client = get_gemini_client(api_key.strip())
    progress = st.progress(0, text="Initialising…")
    
    # Pass the stream and role context to your engine functions
    research_summary = run_research_pass(client, selected_roles, progress)
    extracted = run_extraction_pass(client, selected_roles, research_summary, progress)
    enhanced = run_enhancement_pass(client, extracted, progress)

    st.success("✅ Architecture complete. Customize your details below.")
    
    # ── EDITABLE FIELDS & PREVIEW ──────────────────────────
    final_data = render_editable_fields(enhanced)
    render_preview(final_data)

    # ── DOWNLOADS ──────────────────────────────────────────
    st.markdown("### 📥 Download Your Masterpiece")
    # ... [Keep your existing download button logic here] ...

# --- HELPER FUNCTIONS ---
# Ensure you include your existing render_preview and render_editable_fields functions below
