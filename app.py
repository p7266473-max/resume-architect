"""
Resume Architect Factory — v2.0 (Modular Refactor)
==================================================
Production-ready Streamlit application that transforms raw career history
into executive-quality resumes using Google Gemini AI.
"""

import logging
import os

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
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: linear-gradient(155deg, #0a0a1a 0%, #0f0c29 35%, #1a1a2e 70%, #16213e 100%);
  }

  /* ---- Hero ---- */
  .hero {
    text-align: center;
    padding: 2.5rem 0 1rem;
  }
  .hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c084fc 0%, #818cf8 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 0.5rem;
  }
  .hero-sub {
    font-size: 1.1rem;
    color: #94a3b8;
    font-weight: 400;
    margin: 0;
  }

  /* ---- Section labels ---- */
  .section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.35rem;
  }

  /* ---- Primary button ---- */
  div.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%) !important;
    color: #fff !important;
    border: none !important;
    padding: 0.8rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    width: 100% !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.4) !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.3px !important;
  }
  div.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.55) !important;
  }
  div.stButton > button:active { transform: translateY(1px) !important; }

  /* ---- Download buttons ---- */
  div.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #fff !important;
    border: none !important;
    padding: 0.7rem 1.5rem !important;
    font-size: 0.97rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(5,150,105,0.35) !important;
    transition: all 0.25s ease !important;
  }
  div.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(5,150,105,0.5) !important;
  }

  /* ---- Sidebar ---- */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#15152b 0%,#0d0d1c 100%);
    border-right: 1px solid #1e1e38;
  }

  /* ---- Text area ---- */
  .stTextArea textarea {
    background: #141428 !important;
    color: #e2e8f0 !important;
    border: 1px solid #2e2e50 !important;
    border-radius: 12px !important;
    font-size: 0.94rem !important;
  }
  .stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.2) !important;
  }

  /* ---- Expander ---- */
  .streamlit-expanderHeader {
    background: #141428 !important;
    border: 1px solid #2e2e50 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }

  /* ---- Divider ---- */
  .glow-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #7c3aed 30%, #38bdf8 70%, transparent);
    margin: 1.5rem 0;
  }

  /* ---- Tag chips ---- */
  .skill-chip {
    display: inline-block;
    background: rgba(124,58,237,0.18);
    color: #c084fc;
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 2px;
  }

  /* ---- Warning / char count ---- */
  .char-count { font-size: 0.78rem; color: #64748b; text-align: right; }
  .char-warn  { font-size: 0.78rem; color: #f59e0b; text-align: right; }
  .char-error { font-size: 0.78rem; color: #ef4444; text-align: right; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div class="hero">
  <div class="hero-title">{APP_ICON} {APP_TITLE}</div>
  <p class="hero-sub">{APP_SUBTITLE}</p>
</div>
<hr class="glow-divider">
""", unsafe_allow_html=True)

# ============================================================
# PREVIEW
# ============================================================

def render_preview(data: dict) -> None:
    """Render a rich, read-only in-app preview of the resume."""
    with st.expander("📄 Resume Preview", expanded=True):
        name = data.get("Name", "").strip()
        if name:
            st.markdown(f"<h2 style='margin-bottom:2px'>{name}</h2>", unsafe_allow_html=True)
        contact_items = [
            data.get("Email", ""), data.get("Phone", ""),
            data.get("LinkedIn", ""), data.get("Location", ""),
        ]
        contact_line = "  &nbsp;|&nbsp;  ".join(f"`{c}`" for c in contact_items if c)
        if contact_line:
            st.markdown(contact_line)
        st.markdown("---")

        st.markdown("### 📋 Professional Summary")
        st.info(data.get("Summary", ""))
        st.markdown("---")

        st.markdown("### 💼 Professional Experience")
        for exp in data.get("Experience", []):
            st.markdown(f"**{exp.get('Role')}** &nbsp;·&nbsp; *{exp.get('Company')}*")
            dur = exp.get("Duration", "")
            if dur:
                st.caption(dur)
            for ach in exp.get("Achievements", []):
                st.markdown(f"- {ach}")
            st.markdown("")
        st.markdown("---")

        st.markdown("### 🛠️ Key Skills")
        skills_html = "".join(f'<span class="skill-chip">{s}</span>' for s in data.get("Skills", []))
        st.markdown(skills_html, unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("### 🎓 Education & Certifications")
        for edu in data.get("Education", []):
            st.markdown(f"- {edu}")

# ============================================================
# EDITABLE FIELDS
# ============================================================

def render_editable_fields(data: dict) -> dict:
    """Display editable Streamlit widgets pre-filled with AI output.
    Returns the user-modified version of the resume dict."""
    st.markdown("#### ✏️ Review & Edit Before Downloading")
    st.caption("All fields below are pre-filled by Gemini. Edit anything before exporting.")

    edited = dict(data)

    with st.expander("👤 Contact Information", expanded=False):
        c1, c2 = st.columns(2)
        edited["Name"] = c1.text_input("Full Name", value=data.get("Name", ""), key="edit_name")
        edited["Email"] = c2.text_input("Email", value=data.get("Email", ""), key="edit_email")
        c3, c4 = st.columns(2)
        edited["Phone"] = c3.text_input("Phone", value=data.get("Phone", ""), key="edit_phone")
        edited["Location"] = c4.text_input("Location", value=data.get("Location", ""), key="edit_location")
        edited["LinkedIn"] = st.text_input("LinkedIn URL", value=data.get("LinkedIn", ""), key="edit_linkedin")

    with st.expander("📋 Professional Summary", expanded=False):
        edited["Summary"] = st.text_area(
            "Summary (80-120 words recommended)",
            value=data.get("Summary", ""),
            height=130,
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
                height=120,
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

    with st.expander("🛠️ Skills", expanded=False):
        skills_text = st.text_area(
            "Skills (one per line)",
            value="\n".join(data.get("Skills", [])),
            height=130,
            key="edit_skills",
        )
        edited["Skills"] = [s.strip() for s in skills_text.split("\n") if s.strip()]

    with st.expander("🎓 Education & Certifications", expanded=False):
        edu_text = st.text_area(
            "Education (one per line)",
            value="\n".join(data.get("Education", [])),
            height=100,
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
    "🎨 Resume Theme",
    options=THEMES,
    index=0,
    help="Modern-Tech: purple/teal. Classic-Executive: navy. ATS-Friendly: black/white.",
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
    "<small style='color:#4a5568;'>Powered by Gemini 2.5 Flash &bull; python-docx &bull; v2.0</small>",
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
    height=230,
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
build_clicked: bool = st.button("🚀 Build Professional Resume")

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
    st.success("🎉 **Resume built successfully! Review, edit, and download below.**")

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
    st.markdown("### 📥 Download Your Resume")
    dl1, dl2, dl3 = st.columns(3)

    with dl1:
        if docx_bytes:
            st.download_button(
                label="📄 Word Document (.docx)",
                data=docx_bytes,
                file_name="resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    with dl2:
        st.download_button(
            label="📝 Markdown (.md)",
            data=md_content.encode("utf-8"),
            file_name="resume.md",
            mime="text/markdown",
        )

    with dl3:
        st.download_button(
            label="📃 ATS Plain Text (.txt)",
            data=ats_content.encode("utf-8"),
            file_name="resume_ats.txt",
            mime="text/plain",
        )
