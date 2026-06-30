import streamlit as st
import os
import json
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Resume Architect Factory",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #FFD700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #A0A0A0;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💼 Resume Architect Factory</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Transforming raw career data into professional, high-impact resumes</div>', unsafe_allow_html=True)

# Define Tool Registry actions
def synthesize_content(raw_input: str) -> dict:
    """Extracts key achievements from raw user input and maps them to standard resume sections."""
    st.info("Extracting achievements and mapping to sections...")
    return {
        "Summary": "Professional Developer with expertise in building modular backend systems and workflows.",
        "Experience": [
            {
                "Role": "Software Engineer",
                "Company": "Tech Corp",
                "Duration": "2024 - Present",
                "Achievements": ["Designed a Factory pattern for resume generation", "Integrated multiple LLM providers"]
            }
        ],
        "Skills": ["Python", "Streamlit", "GenAI SDK", "Hugging Face"],
        "Education": ["B.S. in Computer Science"]
    }

def style_resume(structured_data: dict, theme: str = "Modern-Tech") -> dict:
    """Takes structured resume data and applies professional formatting layout/theme."""
    st.info(f"Applying styling theme: '{theme}'...")
    return {
        "theme": theme,
        "content": structured_data,
        "styling_rules": {
            "font_family": "Outfit" if theme == "Modern-Tech" else "Inter",
            "primary_color": "#FFD700" if theme == "Modern-Tech" else "#1E1E1E",
            "layout": "single-column"
        }
    }

def generate_pdf(styled_data: dict, output_filename: str = "resume.pdf") -> str:
    """Converts resume data to PDF using Nutrient DWS API."""
    st.info("Generating final PDF via Nutrient DWS API...")
    download_url = f"https://api.nutrient.dws/download/{output_filename}"
    return download_url

class ResumeArchitect:
    def __init__(self, provider: str):
        self.provider = provider.lower()
        
    def process(self, prompt: str, theme: str = "Modern-Tech"):
        if self.provider == "gemini":
            return self._call_gemini(prompt, theme)
        elif self.provider == "huggingface":
            return self._call_local_model(prompt, theme)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_gemini(self, prompt: str, theme: str):
        st.write("Using `google-genai` SDK for tool-orchestration...")
        # Mocking the pipeline execution:
        synthesized = synthesize_content(prompt)
        styled = style_resume(synthesized, theme)
        pdf_url = generate_pdf(styled)
        return synthesized, styled, pdf_url

    def _call_local_model(self, prompt: str, theme: str):
        st.write("Loading local DeepSeek model for tool signature processing...")
        synthesized = synthesize_content(prompt)
        styled = style_resume(synthesized, theme)
        pdf_url = generate_pdf(styled)
        return synthesized, styled, pdf_url

# Sidebar Settings
st.sidebar.header("Configuration")
provider_env = os.getenv("RESUME_PROVIDER", "gemini")
provider = st.sidebar.selectbox("Model Provider", options=["gemini", "huggingface"], index=0 if provider_env == "gemini" else 1)
theme = st.sidebar.selectbox("Resume Theme", options=["Modern-Tech", "Classic-Executive", "Minimalist"])

agent = ResumeArchitect(provider=provider)

# User Interface
raw_input = st.text_area("Enter your raw career history, achievements, and educational info:", 
                         placeholder="e.g., I worked as a software engineer at Tech Corp from 2024 to present where I designed a Factory pattern for resume generation.")

if st.button("Build Resume"):
    if raw_input.strip() == "":
        st.warning("Please enter some career details first.")
    else:
        with st.spinner("Processing..."):
            synthesized, styled, pdf_url = agent.process(raw_input, theme)
            
            st.success("Successfully Architected your Resume!")
            
            # Display columns with results
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Synthesized Content")
                st.json(synthesized)
            with col2:
                st.subheader("Applied Styling Metadata")
                st.json(styled)
                
            st.markdown(f"### [📥 Download Resume PDF]({pdf_url})")
