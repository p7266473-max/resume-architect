"""
Resume Architect Factory — v2.0 (Premium Executive UI Edition)
==============================================================
Production-ready Streamlit application that transforms raw career history
into executive-quality resumes using Google Gemini AI.
"""

import logging
import os
import time

import streamlit as st

from core.prompts import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    THEMES,
    PLACEHOLDER_TEXT,
    MIN_INPUT_CHARS,
    MAX_INPUT_CHARS,
)
from core.engine import (
    get_gemini_client,
    run_research_pass,
    run_extraction_pass,
    run_enhancement_pass,
)
from core.doc_maker import (
    extract_text_from_docx,
    extract_text_from_pdf,
    generate_docx_bytes,
    generate_markdown,
    generate_ats_text,
)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("resume_architect")

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #FAFAFA; /* Elegant very light gray/white */
    color: #1A1A1A;
  }

  /* ---- Hero ---- */
  .hero-container {
    text-align: center;
    padding: 3rem 1rem 2rem;
    background: url('https://images.unsplash.com/photo-1497215728101-856f4ea42174?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80') no-repeat center center;
    background-size: cover;
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    margin-bottom: 3rem;
    border: 1px solid #EAEAEA;
    position: relative;
    overflow: hidden;
  }
  
  .hero-overlay {
    background: rgba(255, 255, 255, 0.90);
    backdrop-filter: blur(10px);
    padding: 3.5rem 2rem;
    border-radius: 16px;
    margin: 1rem auto;
    max-width: 850px;
    border: 1px solid rgba(212, 175, 55, 0.4); /* Subtle gold border */
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  }

  .hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.8rem;
    font-weight: 700;
    color: #0A192F; /* Deep Navy */
    letter-spacing: -0.5px;
    line-height: 1.2;
    margin-bottom: 1rem;
  }
  
  .hero-title span {
    background: linear-gradient(135deg, #D4AF37 0%, #AA8000 100%); /* Gold gradient */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero-sub {
    font-size: 1.25rem;
    color: #4A5568;
    font-weight: 400;
    margin: 0 auto;
    max-width: 650px;
    line-height: 1.6;
  }

  /* ---- Primary button ---- */
  div.stButton > button {
    background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    padding: 1rem 2.5rem !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    border-radius: 50px !important;
    width: 100% !important;
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.4) !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase;
  }
  div.stButton > button:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 15px 35px rgba(212, 175, 55, 0.6) !important;
  }
  div.stButton > button:active { transform: translateY(2px) !important; }

  /* ---- Download buttons ---- */
  div.stDownloadButton > button {
    background: #0A192F !important; /* Navy */
    color: #D4AF37 !important; /* Gold text */
    border: 1px solid #D4AF37 !important;
    padding: 0.8rem 1.8rem !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    width: 100% !important;
    box-shadow: 0 8px 20px rgba(10, 25, 47, 0.15) !important;
    transition: all 0.25s ease !important;
  }
  div.stDownloadButton > button:hover {
    background: #112240 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(10, 25, 47, 0.25) !important;
  }

  /* ---- Sidebar ---- */
  section[data-testid="stSidebar"] {
    background: #F4F7F6;
    border-right: 1px solid #E2E8F0;
  }
  section[data-testid="stSidebar"] .stMarkdown {
    color: #2D3748;
  }

  /* ---- Text area ---- */
  .stTextArea textarea {
    background: #FFFFFF !important;
    color: #1A202C !important;
    border: 2px solid #E2E8F0 !important;
    border-radius: 16px !important;
    font-size: 1.05rem !important;
    padding: 1rem !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    transition: all 0.2s ease;
  }
  .stTextArea textarea:focus {
    border-color: #D4AF37 !important;
    box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.15) !important;
  }

  /* ---- Expander ---- */
  .streamlit-expanderHeader {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: #0A192F !important;
  }

  /* ---- Divider ---- */
  .glow-divider {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #D4AF37 30%, #AA8000 70%, transparent);
    margin: 2.5rem 0;
    opacity: 0.6;
  }

  /* ---- Tag chips ---- */
  .skill-chip {
    display: inline-block;
    background: #FDFBF7;
    color: #AA8000;
    border: 1px solid rgba(212, 175, 55, 0.4);
    border-radius: 999px;
    padding: 6px 18px;
    font-size: 0.9rem;
    font-weight: 600;
    margin: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
  }

  /* ---- Warning / char count ---- */
  .char-count { font-size: 0.9rem; color: #718096; text-align: right; font-weight: 500; }
  .char-warn  { font-size: 0.9rem; color: #DD6B20; text-align: right; font-weight: 600; }
  .char-error { font-size: 0.9rem; color: #E53E3E; text-align: right; font-weight: 600; }
  
  /* Additional polish */
  div[data-testid="stMarkdownContainer"] h2, div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h4 {
    color: #0A192F !important;
    font-family: 'Playfair Display', serif;
  }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero-container">
  <div class="hero-overlay">
    <div class="hero-title">Elevate Your Career to <br><span>Executive Class</span></div>
    <p class="hero-sub">Transform your raw career history into a prestigious, world-class executive resume. Experience the power of McKinsey-standard professional branding and outshine the competition.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PREVIEW
# ============================================================

def render_preview(data: dict) -> None:
    """Render a rich, read-only in-app preview of the resume."""
    with st.expander("📄 Executive Resume Preview", expanded=True):
        name = data.get("Name", "").strip()
        if name:
            st.markdown(f"<h2 style='text-align:center; font-size: 2.5rem; margin-bottom: 0;'>{name}</h2>", unsafe_allow_html=True)
        
        contact_items = [
            data.get("Location", ""), data.get("Phone", ""),
            data.get("Email", ""), data.get("LinkedIn", "")
        ]
        contact_line = "  &nbsp;|&nbsp;  ".join(f"{c}" for c in contact_items if c)
        if contact_line:
            st.markdown(f"<p style='text-align:center; color:#555;'>{contact_line}</p>", unsafe_allow_html=True)
        
        st.markdown('<hr class="glow-divider" style="margin: 1rem 0;">', unsafe_allow_html=True)

        st.markdown("### 📋 Professional Summary")
        st.info(data.get("Summary", ""))
        
        st.markdown('<hr class="glow-divider" style="margin: 1.5rem 0;">', unsafe_allow_html=True)

        st.markdown("### 💼 Professional Experience")
        for exp in data.get("Experience", []):
            role = exp.get('Role', '')
            company = exp.get('Company', '')
            duration = exp.get('Duration', '')
            
            st.markdown(f"**{role}** &nbsp;|&nbsp; *{company}* <span style='float:right;'>*{duration}*</span>", unsafe_allow_html=True)
            
            for ach in exp.get("Achievements", []):
                st.markdown(f"- {ach}")
            st.markdown("")
        
        st.markdown('<hr class="glow-divider" style="margin: 1.5rem 0;">', unsafe_allow_html=True)

        st.markdown("### 🛠️ Core Competencies & Skills")
        skills_html = "".join(f'<span class="skill-chip">{s}</span>' for s in data.get("Skills", []))
        st.markdown(skills_html, unsafe_allow_html=True)
        
        st.markdown('<hr class="glow-divider" style="margin: 1.5rem 0;">', unsafe_allow_html=True)

        st.markdown("### 🎓 Education & Certifications")
        for edu in data.get("Education", []):
            st.markdown(f"- **{edu}**")

# ============================================================
# EDITABLE FIELDS
# ============================================================

def render_editable_fields(data: dict) -> dict:
    """Display editable Streamlit widgets pre-filled with AI output."""
    st.markdown("### ✏️ Review & Perfect Your Profile")
    st.caption("All fields below have been masterfully curated by the AI. Edit anything before exporting your final document.")

    edited = dict(data)

    with st.expander("👤 Contact Information", expanded=False):
        c1, c2 = st.columns(2)
        edited["Name"] = c1.text_input("Full Name", value=data.get("Name", ""), key="edit_name")
        edited["Email"] = c2.text_input("Email", value=data.get("Email", ""), key="edit_email")
        c3, c4 = st.columns(2)
        edited["Phone"] = c3.text_input("Phone", value=data.get("Phone", ""), key="edit_phone")
        edited["Location"] = c4.text_input("Location", value=data.get("Location", ""), key="edit_location")
        edited["LinkedIn"] = st.text_input("LinkedIn URL", value=data.get("LinkedIn", ""), key="edit_linkedin")

    with st.expander("📋 Executive Summary", expanded=False):
        edited["Summary"] = st.text_area(
            "Summary (80-120 words recommended)",
            value=data.get("Summary", ""),
            height=150,
            key="edit_summary",
        )

    with st.expander("💼 Experience", expanded=False):
        edited_exp: list[dict] = []
        for i, exp in enumerate(data.get("Experience", [])):
            st.markdown(f"**Role {i+1}**")
            ec1, ec2, ec3 = st.columns([3, 3, 2])
            role = ec1.text_input("Job Title", value=exp.get("Role", ""), key=f"role_{i}")
            company = ec2.text_input("Company", value=exp.get("Company", ""), key=f"company_{i}")
            duration = ec3.text_input("Duration", value=exp.get("Duration", ""), key=f"duration_{i}")
            achievements_text = st.text_area(
                "Achievements (one per line)",
                value="\n".join(exp.get("Achievements", [])),
                height=180,
                key=f"achievements_{i}",
            )
            edited_exp.append({
                "Role": role,
                "Company": company,
                "Duration": duration,
                "Achievements": [a.strip() for a in achievements_text.split("\n") if a.strip()],
            })
            st.markdown("---")
        edited["Experience"] = edited_exp

    with st.expander("🛠️ Core Competencies", expanded=False):
        skills_text = st.text_area(
            "Skills (one per line)",
            value="\n".join(data.get("Skills", [])),
            height=150,
            key="edit_skills",
        )
        edited["Skills"] = [s.strip() for s in skills_text.split("\n") if s.strip()]

    with st.expander("🎓 Education & Certifications", expanded=False):
        edu_text = st.text_area(
            "Education (one per line)",
            value="\n".join(data.get("Education", [])),
            height=120,
            key="edit_education",
        )
        edited["Education"] = [e.strip() for e in edu_text.split("\n") if e.strip()]

    return edited

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## ⚙️ Configuration")

api_key: str = st.sidebar.text_input(
    "🔑 Gemini API Key",
    value=os.environ.get("GEMINI_API_KEY", ""),
    type="password",
    help="Get your key at https://aistudio.google.com/apikey",
)

theme: str = st.sidebar.selectbox(
    "🎨 Output Theme",
    options=THEMES,
    index=1,
    help="Select the color palette for your final Word document.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**📤 Upload Existing Resume**")
uploaded_file = st.sidebar.file_uploader(
    "Upload .docx or .pdf to extract text automatically",
    type=["docx", "pdf"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small style='color:#718096;'>Powered by Gemini 2.5 Flash &bull; python-docx &bull; Premium Edition</small>",
    unsafe_allow_html=True,
)

# ============================================================
# MAIN INPUT AREA
# ============================================================

# Pre-fill from upload
uploaded_text: str = ""
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    if uploaded_file.name.lower().endswith(".docx"):
        uploaded_text = extract_text_from_docx(file_bytes)
    elif uploaded_file.name.lower().endswith(".pdf"):
        uploaded_text = extract_text_from_pdf(file_bytes)
    if uploaded_text:
        st.sidebar.success(f"✅ Extracted {len(uploaded_text):,} characters from {uploaded_file.name}")
        logger.info("Extracted %d chars from uploaded file: %s", len(uploaded_text), uploaded_file.name)
    else:
        st.sidebar.warning("⚠️ Could not extract text. Try copy-pasting instead.")

raw_input: str = st.text_area(
    "📝 Paste your raw career history",
    value=uploaded_text,
    height=280,
    placeholder=PLACEHOLDER_TEXT,
    help=f"Minimum {MIN_INPUT_CHARS} characters. Maximum {MAX_INPUT_CHARS:,} characters.",
)

# Character counter + validation hint
char_count = len(raw_input)
if char_count == 0:
    st.markdown(f'<p class="char-count">0 / {MAX_INPUT_CHARS:,} characters</p>', unsafe_allow_html=True)
elif char_count < MIN_INPUT_CHARS:
    st.markdown(f'<p class="char-warn">⚠️ {char_count} / {MAX_INPUT_CHARS:,} — too short (min {MIN_INPUT_CHARS})</p>', unsafe_allow_html=True)
elif char_count > MAX_INPUT_CHARS:
    st.markdown(f'<p class="char-error">❌ {char_count:,} / {MAX_INPUT_CHARS:,} — too long (trim to {MAX_INPUT_CHARS:,})</p>', unsafe_allow_html=True)
else:
    st.markdown(f'<p class="char-count">✓ {char_count:,} / {MAX_INPUT_CHARS:,} characters</p>', unsafe_allow_html=True)

st.markdown("")
build_clicked: bool = st.button("🚀 Transform Into Executive Resume")

# ============================================================
# PIPELINE
# ============================================================

if build_clicked:
    # Input validation
    if not raw_input.strip():
        st.warning("⚠️ Please paste or upload your career history first.")
        st.stop()
    if char_count < MIN_INPUT_CHARS:
        st.warning(f"⚠️ Input is too short ({char_count} chars). Please add more detail — minimum {MIN_INPUT_CHARS} characters.")
        st.stop()
    if char_count > MAX_INPUT_CHARS:
        st.error(f"❌ Input is too long ({char_count:,} chars). Please trim to under {MAX_INPUT_CHARS:,} characters.")
        st.stop()
    if not api_key.strip():
        st.error("🔑 Please enter your Gemini API Key in the sidebar.")
        st.stop()

    # Client
    try:
        client = get_gemini_client(api_key.strip())
    except Exception as exc:
        logger.error("Client init failed: %s", exc)
        st.error(f"❌ Failed to initialise Gemini client: {exc}")
        st.stop()

    progress = st.progress(0, text="Initialising pipeline…")
    status = st.empty()

    # Web Research Grounding Pass
    progress.progress(5, text="Web Research: Gathering top resume guidelines…")
    with st.spinner("Researching the best resumes via Google Search grounding…"):
        research_summary = run_research_pass(client, raw_input, status)

    # Pass 1
    progress.progress(15, text="Pass 1: Extracting structured content…")
    with st.spinner("Analysing career history & incorporating research…"):
        extracted = run_extraction_pass(client, raw_input, research_summary, status)

    if extracted is None:
        progress.progress(100, text="Pipeline failed.")
        st.stop()

    progress.progress(55, text="Pass 1 complete ✓")
    status.success("✅ Pass 1 — Structured extraction complete.")

    # Pass 2
    progress.progress(60, text="Pass 2: Enhancing executive language…")
    with st.spinner("Elevating resume language…"):
        enhanced = run_enhancement_pass(client, extracted, status)

    progress.progress(85, text="Pass 2 complete ✓")
    status.success("✅ Pass 2 — Executive enhancement complete.")

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.success("🎉 **Masterpiece complete! Review, edit, and download your executive resume below.**")

    # ── EDITABLE FIELDS ────────────────────────────────────
    final_data = render_editable_fields(enhanced)

    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)

    # ── PREVIEW ────────────────────────────────────────────
    render_preview(final_data)

    progress.progress(90, text="Generating export files…")

    # ── GENERATE ALL EXPORTS ───────────────────────────────
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

    # ── DOWNLOAD BUTTONS ───────────────────────────────────
    st.markdown("### 📥 Download Your Masterpiece")
    dl1, dl2, dl3 = st.columns(3)

    with dl1:
        if docx_bytes:
            st.download_button(
                label="📄 Premium Word Document (.docx)",
                data=docx_bytes,
                file_name="Executive_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    with dl2:
        st.download_button(
            label="📝 Markdown (.md)",
            data=md_content.encode("utf-8"),
            file_name="Executive_Resume.md",
            mime="text/markdown",
        )

    with dl3:
        st.download_button(
            label="📃 ATS Plain Text (.txt)",
            data=ats_content.encode("utf-8"),
            file_name="Executive_Resume_ATS.txt",
            mime="text/plain",
        )
