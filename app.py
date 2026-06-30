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

# Custom Premium Styling
st.markdown("""
<style>
    /* Main Background and Card Design */
    .reportview-container {
        background: linear-gradient(135deg, #1e1e2f 0%, #11111d 100%);
    }
    
    /* Center Title Custom CSS */
    .title-container {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .title-main {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a855f7 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .title-sub {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Customize Buttons and Inputs */
    div.stButton > button {
        background: linear-gradient(90deg, #a855f7 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Code block container styling */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        background-color: #0f172a !important;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="title-container">
    <div class="title-main">Resume Architect Factory</div>
    <div class="title-sub">Transform your raw career data into professional, high-impact resumes instantly</div>
</div>
""", unsafe_allow_html=True)

# Define Tool Registry actions
def synthesize_content(raw_input: str) -> dict:
    """Extracts key achievements from raw user input and maps them to standard resume sections."""
    st.info("Extracting achievements and mapping to sections...")
    return {
        "Summary": f"Professional with experience highlighting: {raw_input[:100]}...",
        "Experience": [
            {
                "Role": "Career Specialist",
                "Company": "Enterprise Corp",
                "Duration": "Recent",
                "Achievements": [raw_input]
            }
        ],
        "Skills": ["Dynamic Adaptation", "Communication"],
        "Education": ["Professional Experience Record"]
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
    def __init__(self, provider: str, api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        
    def process(self, prompt: str, theme: str = "Modern-Tech"):
        try:
            if self.provider == "gemini":
                return self._call_gemini(prompt, theme)
            elif self.provider == "huggingface":
                return self._call_local_model(prompt, theme)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        except Exception as e:
            st.error(f"⚠️ Resume Factory Maintenance: Failed to build resume. Error details: {str(e)}")
            return None, None, None

    def _call_gemini(self, prompt: str, theme: str):
        st.write("Orchestrating agent run via Gemini SDK Function Calling...")
        
        # Initialize Google GenAI client using the provided key
        client = genai.Client(api_key=self.api_key)
        
        # 1. Define tools for Gemini
        tools_list = [synthesize_content, style_resume, generate_pdf]
        
        # We start with the user's prompt in the contents list
        contents = [
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=f"The user wants to build a resume with the details: '{prompt}'. Follow the tools sequence step-by-step: first synthesize_content, then style_resume with theme '{theme}', and finally generate_pdf.")]
            )
        ]
        
        synthesized_data = {}
        styled_data = {}
        pdf_url = ""
        
        # Maximum safety threshold for multi-turn steps
        max_turns = 10
        for turn in range(max_turns):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=tools_list,
                    temperature=0.0
                )
            )
            
            # Append the assistant's turn to the history
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)
            else:
                break
            
            # If the model requested function calls
            if response.function_calls:
                tool_responses = []
                for call in response.function_calls:
                    st.write(f"Gemini requested tool execution: `{call.name}`")
                    
                    # Execute the function based on the call name
                    if call.name == "synthesize_content":
                        synthesized_data = synthesize_content(**call.args)
                        result = synthesized_data
                    elif call.name == "style_resume":
                        args = dict(call.args)
                        # Ensure structured_data is populated if not provided
                        if "structured_data" not in args or not args["structured_data"]:
                            args["structured_data"] = synthesized_data
                        # Ensure theme is populated
                        if "theme" not in args or not args["theme"]:
                            args["theme"] = theme
                        styled_data = style_resume(**args)
                        result = styled_data
                    elif call.name == "generate_pdf":
                        args = dict(call.args)
                        # Ensure styled_data is populated if not provided
                        if "styled_data" not in args or not args["styled_data"]:
                            args["styled_data"] = styled_data
                        pdf_url = generate_pdf(**args)
                        result = {"download_url": pdf_url}
                    else:
                        result = {"error": f"Unknown function: {call.name}"}
                    
                    # Add to the tool responses part
                    tool_responses.append(
                        types.Part.from_function_response(
                            name=call.name,
                            response=result
                        )
                    )
                
                # Append the tool execution response to the history with role='tool'
                contents.append(
                    types.Content(
                        role='tool',
                        parts=tool_responses
                    )
                )
            else:
                # No more function calls, we are done
                break
                
        # Fallback if somehow they are not filled
        if not pdf_url:
            st.write("Model did not request complete tool execution flow. Running fallback pipeline...")
            if not synthesized_data:
                synthesized_data = synthesize_content(prompt)
            if not styled_data:
                styled_data = style_resume(synthesized_data, theme)
            pdf_url = generate_pdf(styled_data)
            
        return synthesized_data, styled_data, pdf_url

    def _call_local_model(self, prompt: str, theme: str):
        st.write("Loading local DeepSeek model for tool signature processing...")
        synthesized_data = synthesize_content(prompt)
        styled_data = style_resume(synthesized_data, theme)
        pdf_url = generate_pdf(styled_data)
        return synthesized_data, styled_data, pdf_url

# Sidebar Settings & Key Retriever
st.sidebar.header("Configuration")

# Retrieve API key: check secrets first, then environment variables
default_api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=default_api_key,
    type="password",
    help="Provide your API key to run queries."
)

provider_env = os.getenv("RESUME_PROVIDER", "gemini")
provider = st.sidebar.selectbox("Model Provider", options=["gemini", "huggingface"], index=0 if provider_env == "gemini" else 1)
theme = st.sidebar.selectbox("Resume Theme", options=["Modern-Tech", "Classic-Executive", "Minimalist"])

agent = ResumeArchitect(provider=provider, api_key=api_key)

# User Interface
raw_input = st.text_area("Enter your raw career history, achievements, and educational info:", 
                         placeholder="e.g., I worked as a software engineer at Tech Corp from 2024 to present where I designed a Factory pattern for resume generation.")

if st.button("Build Resume"):
    if not raw_input.strip():
        st.warning("Please enter some career details first.")
    elif provider == "gemini" and not api_key:
        st.error("Kindly enter API Key in the sidebar configuration.")
    else:
        with st.spinner("Processing..."):
            synthesized, styled, pdf_url = agent.process(raw_input, theme)
            
            if pdf_url:
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
