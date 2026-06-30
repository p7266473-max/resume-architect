import streamlit as st
import os
import json
from google import genai
from google.genai import types
from docx import Document

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
    st.info("Synthesizing achievements and mapping to sections...")
    
    # Initialize Google GenAI client (picks up GEMINI_API_KEY from environment)
    try:
        client = genai.Client()
        prompt = f"""
        Analyze the following raw career history and achievements:
        "{raw_input}"
        
        Extract and structure this into a high-quality professional resume.
        Provide the response in JSON format matching this schema:
        {{
          "Summary": "A strong 2-3 sentence professional summary",
          "Experience": [
            {{
              "Role": "Job Title",
              "Company": "Company Name",
              "Duration": "Employment Dates",
              "Achievements": [
                "Specific, action-oriented achievement 1",
                "Specific, action-oriented achievement 2"
              ]
            }}
          ],
          "Skills": ["Skill 1", "Skill 2"],
          "Education": ["Education/Certification 1"]
        }}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.warning(f"GenAI synthesis failed, falling back to basic extraction: {str(e)}")
        return {
            "Summary": f"Professional with experience highlighting: {raw_input[:100]}...",
            "Experience": [
                {
                    "Role": "Specialist",
                    "Company": "Enterprise Corp",
                    "Duration": "Recent",
                    "Achievements": [raw_input]
                }
            ],
            "Skills": ["Professional Experience"],
            "Education": ["Degree/Certification"]
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

def generate_docx(styled_data: dict, output_filename: str = "resume.docx") -> str:
    """Generates a professional DOCX file using pure Python (python-docx). No system dependencies."""
    st.info("Generating final Word DOCX via python-docx...")
    
    doc = Document()
    content = styled_data.get("content", {})
    
    # Title
    doc.add_heading(f"{styled_data.get('theme', 'Resume')}", 0)
    
    # Summary
    doc.add_heading('Professional Summary', level=1)
    doc.add_paragraph(content.get("Summary", ""))
    
    # Experience
    doc.add_heading('Professional Experience', level=1)
    for exp in content.get("Experience", []):
        doc.add_heading(f"{exp.get('Role', 'Role')} at {exp.get('Company', 'Company')}", level=2)
        doc.add_paragraph(f"Duration: {exp.get('Duration', '')}")
        for ach in exp.get("Achievements", []):
            doc.add_paragraph(ach, style='List Bullet')
    
    # Skills
    doc.add_heading('Key Skills', level=1)
    doc.add_paragraph(", ".join(content.get("Skills", [])))
    
    # Education
    doc.add_heading('Education & Certifications', level=1)
    for edu in content.get("Education", []):
        doc.add_paragraph(edu, style='List Bullet')
    
    output_path = os.path.join(os.getcwd(), output_filename)
    doc.save(output_path)
    return output_path


class ResumeArchitect:
    def __init__(self, provider: str, api_key: str = None):
        self.provider = provider.lower()
        self.api_key = api_key
        
    def process(self, prompt: str, theme: str = "Modern-Tech"):
        try:
            # Set API key in environment variable so tools can pick it up
            if self.api_key:
                os.environ["GEMINI_API_KEY"] = self.api_key
            return self._call_gemini(prompt, theme)
        except Exception as e:
            st.error(f"⚠️ Resume Factory Maintenance: Failed to build resume. Error details: {str(e)}")
            return None, None, None

    def _check_quality(self, client, raw_input: str, synthesized_data: dict) -> tuple[bool, str]:
        st.info("Evaluating resume quality against professional standards...")
        
        prompt = f"""
        Evaluate the following synthesized resume content against professional career standards.
        Raw Input: "{raw_input}"
        Synthesized Content: {json.dumps(synthesized_data, indent=2)}
        
        Standards:
        1. Professional Summary: Must be a detailed description (at least two sentences) and not a generic placeholder or short phrase.
        2. Achievements: Experience achievements must be specific, action-oriented, and directly related to the input. They must not contain mock data like "civil engineer" unless the input explicitly specifies that.
        3. Education & Skills: Must be realistic and parsed/inferred from the raw input.
        
        If the synthesized content contains default mock placeholders or is extremely generic/short, return is_valid as false.
        
        Provide your evaluation in JSON format:
        {{
          "is_valid": true or false,
          "feedback": "Details on what failed or 'Success' if valid"
        }}
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            res_json = json.loads(response.text)
            # Ensure bool type
            is_valid = bool(res_json.get("is_valid", False))
            return is_valid, res_json.get("feedback", "No feedback provided.")
        except Exception as e:
            st.warning(f"Quality checker warning: {str(e)}")
            return True, ""

    def _run_agent_flow(self, client, prompt_text: str, theme: str, tools_list: list):
        # We start with the prompt in the contents list
        contents = [
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=prompt_text)]
            )
        ]
        
        synthesized_data = {}
        styled_data = {}
        docx_path = ""
        
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
                        if "structured_data" not in args or not args["structured_data"]:
                            args["structured_data"] = synthesized_data
                        if "theme" not in args or not args["theme"]:
                            args["theme"] = theme
                        styled_data = style_resume(**args)
                        result = styled_data
                    elif call.name == "generate_docx":
                        args = dict(call.args)
                        if "styled_data" not in args or not args["styled_data"]:
                            args["styled_data"] = styled_data
                        docx_path = generate_docx(**args)
                        result = {"download_url": docx_path}
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
        if not docx_path:
            st.write("Model did not request complete tool execution flow. Running fallback pipeline...")
            if not synthesized_data:
                synthesized_data = synthesize_content(prompt_text)
            if not styled_data:
                styled_data = style_resume(synthesized_data, theme)
            docx_path = generate_docx(styled_data)
            
        return synthesized_data, styled_data, docx_path

    def _call_gemini(self, prompt: str, theme: str):
        st.write("Orchestrating agent run via Gemini SDK Function Calling...")
        
        # Initialize Google GenAI client using the provided key
        client = genai.Client(api_key=self.api_key or None)
        
        # 1. Define tools for Gemini
        tools_list = [synthesize_content, style_resume, generate_docx]
        
        # Run initial flow
        initial_prompt = f"The user wants to build a resume with the details: '{prompt}'. Follow the tools sequence step-by-step: first synthesize_content, then style_resume with theme '{theme}', and finally generate_docx."
        synthesized_data, styled_data, docx_path = self._run_agent_flow(client, initial_prompt, theme, tools_list)
        
        # Quality check
        is_valid, feedback = self._check_quality(client, prompt, synthesized_data)
        if not is_valid:
            st.warning(f"⚠️ Quality check failed: {feedback}. Retrying with feedback-guided prompt...")
            redo_prompt = f"Previous attempt to synthesize resume for details '{prompt}' failed quality standards: {feedback}. Redo the synthesis correcting these issues, then style_resume and generate_docx."
            synthesized_data, styled_data, docx_path = self._run_agent_flow(client, redo_prompt, theme, tools_list)
            
        return synthesized_data, styled_data, docx_path
 

 
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
 
theme = st.sidebar.selectbox("Resume Theme", options=["Modern-Tech", "Classic-Executive", "Minimalist"])

agent = ResumeArchitect(provider="gemini", api_key=api_key)
 
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
            synthesized, styled, docx_path = agent.process(raw_input, theme)
            
            if docx_path:
                st.success("Successfully Architected your Resume!")
                
                # Hidden Raw JSON details as requested (no need to see this, hide it)
                # If needed, the user can inspect/expand:
                with st.expander("Show Technical Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Synthesized Content")
                        st.json(synthesized)
                    with col2:
                        st.subheader("Applied Styling Metadata")
                        st.json(styled)
                    
                with open(docx_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Resume Word Document (DOCX)",
                        data=f,
                        file_name="resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
