import logging
import os
import streamlit as st

from core.prompts import (
    APP_TITLE, APP_SUBTITLE, APP_ICON, THEMES, 
    CAREER_OPTIONS, # Keep existing imports
    STREAM_OPTIONS  # ADD THIS to your core/prompts.py
)
from core.engine import (
    get_gemini_client, run_research_pass, run_extraction_pass, run_enhancement_pass,
)
from core.doc_maker import (
    generate_docx_bytes, generate_markdown, generate_ats_text,
)

# ... [Keep LOGGING, PAGE CONFIG, CSS, HEADER, PREVIEW, EDITABLE FIELDS, SIDEBAR as they were] ...

# ============================================================
# MAIN INPUT AREA (Rectified)
# ============================================================

st.markdown("### 🎯 Configure Your Profile")

# 1. Stream Selection
selected_stream = st.selectbox(
    "Select your academic stream:",
    options=list(STREAM_OPTIONS.keys())
)

# 2. Dynamic Role Selection based on stream
selected_roles = st.multiselect(
    f"What do you want to become as a {selected_stream} student? (Select 1 to 3)",
    options=STREAM_OPTIONS[selected_stream],
    max_selections=3,
    placeholder="Choose your target roles..."
)

st.markdown("")
build_clicked: bool = st.button("🚀 Generate My Future Resume")

# ============================================================
# PIPELINE (Rectified to include Stream context)
# ============================================================

if build_clicked:
    if not selected_roles:
        st.warning("⚠️ Please select at least one future career role.")
        st.stop()
    if not api_key.strip():
        st.error("🔑 Please enter your Gemini API Key in the sidebar.")
        st.stop()

    try:
        client = get_gemini_client(api_key.strip())
    except Exception as exc:
        logger.error("Client init failed: %s", exc)
        st.error(f"❌ Failed to initialise Gemini client: {exc}")
        st.stop()

    progress = st.progress(0, text="Initialising pipeline…")
    status = st.empty()

    # Pass the selected_stream into your engine functions if needed for prompt context
    progress.progress(5, text="Web Research: Finding the best free courses…")
    with st.spinner("Searching the web for top free/open-source certifications for your path…"):
        research_summary = run_research_pass(client, selected_roles, status) # Optionally add selected_stream here

    progress.progress(15, text="Pass 1: Architecting your future resume…")
    with st.spinner("Building your 3-year career trajectory…"):
        extracted = run_extraction_pass(client, selected_roles, research_summary, status)

    if extracted is None:
        progress.progress(100, text="Pipeline failed.")
        st.stop()

    progress.progress(55, text="Pass 1 complete ✓")
    status.success("✅ Architecture complete.")

    progress.progress(60, text="Pass 2: Polishing vocabulary…")
    with st.spinner("Elevating resume language to a top-tier standard…"):
        enhanced = run_enhancement_pass(client, extracted, status)

    progress.progress(85, text="Pass 2 complete ✓")
    status.success("✅ Enhancement complete.")

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.success("🎉 **Your Future Resume is ready! Review, customize the blanks, and download.**")

    final_data = render_editable_fields(enhanced)

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    render_preview(final_data)

    progress.progress(90, text="Generating export files…")
    
    with st.spinner("Building export files…"):
        try:
            docx_bytes = generate_docx_bytes(final_data, theme)
        except Exception as exc:
            logger.error("DOCX generation failed: %s", exc)
            st.error(f"❌ DOCX generation failed: {exc}")
            docx_bytes = b""

        md_content = generate_markdown(final_data)
        ats_content = generate_ats_text(final_data)

    progress.progress(100, text="✅ Ready to download!")
    status.empty()

    st.markdown("### 📥 Download Your Masterpiece")
    dl1, dl2, dl3 = st.columns(3)
    # ... [Keep your existing download button logic] ...
