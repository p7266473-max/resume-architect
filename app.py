import logging
import os
import streamlit as st

# Keep your existing imports
from core.prompts import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, THEMES,
)
from core.engine import (
    get_gemini_client, run_research_pass, run_extraction_pass, run_enhancement_pass,
)
from core.doc_maker import (
    generate_docx_bytes, generate_markdown, generate_ats_text,
)

# ============================================================
# DYNAMIC STREAM CONFIGURATION (Added here to prevent ImportErrors)
# ============================================================
STREAM_OPTIONS = {
    "BSc": ["Software Engineer", "Data Scientist", "Cybersecurity Analyst", "Cloud Architect"],
    "BBA": ["Marketing Manager", "Business Analyst", "Operations Manager", "Financial Strategist"],
    "MBA": ["Product Manager", "Management Consultant", "Business Strategist", "Leadership Trainee"]
}

# ============================================================
# LOGGING, CONFIG, CSS (Keep your original code)
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger("resume_architect")

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

# --- (Insert your original CSS string here exactly as it was) ---

# ============================================================
# HEADER, PREVIEW, EDITABLE FIELDS
# ============================================================
# (Keep your original render_preview and render_editable_fields functions here)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## ⚙️ Configuration")
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
theme = st.sidebar.selectbox("🎨 Output Theme", options=THEMES, index=1)

# ============================================================
# MAIN INPUT AREA
# ============================================================
st.markdown("### 🎯 Career Goals")

# 1. Stream Selection
selected_stream = st.selectbox("Select your academic stream:", options=list(STREAM_OPTIONS.keys()))

# 2. Dynamic Role Selection
selected_roles = st.multiselect(
    f"What do you want to become after graduating with your {selected_stream}? (Select 1 to 3)",
    options=STREAM_OPTIONS[selected_stream],
    max_selections=3
)

build_clicked = st.button("🚀 Generate My Future Resume")

# ============================================================
# PIPELINE
# ============================================================
if build_clicked:
    if not selected_roles or not api_key.strip():
        st.warning("⚠️ Please provide your API Key and select at least one role.")
        st.stop()

    client = get_gemini_client(api_key.strip())
    progress = st.progress(0, text="Initialising…")
    status = st.empty()

    progress.progress(5, text="Web Research…")
    research_summary = run_research_pass(client, selected_roles, status)

    progress.progress(15, text="Architecting resume…")
    extracted = run_extraction_pass(client, selected_roles, research_summary, status)

    progress.progress(60, text="Polishing vocabulary…")
    enhanced = run_enhancement_pass(client, extracted, status)

    st.success("✅ Architecture complete.")
    
    final_data = render_editable_fields(enhanced)
    render_preview(final_data)

    # Export Logic
    docx_bytes = generate_docx_bytes(final_data, theme)
    md_content = generate_markdown(final_data)
    ats_content = generate_ats_text(final_data)

    st.markdown("### 📥 Download Your Masterpiece")
    dl1, dl2, dl3 = st.columns(3)
    dl1.download_button("📄 Word (.docx)", docx_bytes, "Future_Resume.docx")
    dl2.download_button("📝 Markdown (.md)", md_content, "Future_Resume.md")
    dl3.download_button("📃 ATS (.txt)", ats_content, "Future_Resume_ATS.txt")
