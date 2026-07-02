import logging
import os
import streamlit as st

# Core modules (Ensure these exist in your 'core' directory)
from core.prompts import APP_TITLE, APP_ICON, THEMES
from core.engine import (
    get_gemini_client, run_research_pass, run_extraction_pass, run_enhancement_pass,
)
from core.doc_maker import generate_docx_bytes, generate_markdown, generate_ats_text

# --- CONFIGURATION ---
STREAM_CONFIG = {
    "BSc": {
        "roles": ["Software Engineer", "Data Scientist", "Cloud Architect", "AI Engineer"],
        "color": "#3498db"
    },
    "BBA": {
        "roles": ["Business Analyst", "Marketing Strategist", "Operations Manager", "Financial Consultant"],
        "color": "#2ecc71"
    },
    "MBA": {
        "roles": ["Product Manager", "Management Consultant", "Startup Founder", "Corporate Strategist"],
        "color": "#9b59b6"
    }
}

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# --- CSS STYLING ---
st.markdown("""
<style>
    .hero-container { padding: 2rem; border-radius: 15px; background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; font-weight: bold; }
    div[data-testid="stSidebar"] { background-color: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    theme = st.selectbox("Document Theme", options=THEMES)
    st.divider()
    st.info("Ensure your 'core' directory contains the engine and prompts modules.")

# --- HEADER ---
st.markdown('<div class="hero-container"><h1>Future Resume Architect</h1><p>Define your path, craft your future.</p></div>', unsafe_allow_html=True)

# --- MAIN APP FLOW ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Select Your Stream")
    selected_stream = st.radio("Program Type", options=list(STREAM_CONFIG.keys()))
    
    st.subheader("2. Define Goals")
    target_roles = st.multiselect(
        "Target Roles", 
        options=STREAM_CONFIG[selected_stream]["roles"],
        max_selections=3
    )

with col2:
    st.subheader("3. Generation")
    if st.button("🚀 Architect My Resume"):
        if not api_key:
            st.error("API Key missing!")
        elif not target_roles:
            st.warning("Please select at least one role.")
        else:
            try:
                client = get_gemini_client(api_key)
                with st.status("Building your future...", expanded=True) as status:
                    st.write("Researching industry requirements...")
                    res = run_research_pass(client, target_roles, status)
                    st.write("Drafting academic profile...")
                    ext = run_extraction_pass(client, target_roles, res, status)
                    st.write("Polishing content...")
                    final = run_enhancement_pass(client, ext, status)
                    status.update(label="Architecture Complete!", state="complete")
                
                # Render Results
                st.session_state['final_data'] = final
                st.success("Your resume is ready for review below.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- OUTPUT AREA ---
if 'final_data' in st.session_state:
    st.divider()
    # Assuming render_preview is your custom function
    from your_code_file import render_preview, render_editable_fields # Update import
    
    final = render_editable_fields(st.session_state['final_data'])
    render_preview(final)
    
    # Download buttons
    d1, d2, d3 = st.columns(3)
    d1.download_button("Word Doc", generate_docx_bytes(final, theme), "resume.docx")
    d2.download_button("Markdown", generate_markdown(final), "resume.md")
    d3.download_button("ATS Text", generate_ats_text(final), "resume.txt")
