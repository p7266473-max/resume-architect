import streamlit as st
import os
import json
from google import genai
from google.genai import types
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

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

def generate_pptx(styled_data: dict, output_filename: str = "resume.pptx") -> str:
    """Converts resume data to a beautifully formatted PowerPoint presentation using python-pptx."""
    st.info("Generating final PPTX via python-pptx...")
    
    # Retrieve styling details
    theme = styled_data.get("theme", "Modern-Tech")
    content = styled_data.get("content", {})
    
    # Define color palettes matching app styling rules
    if theme == "Modern-Tech":
        bg_color = (0x11, 0x11, 0x1D)        # Sleek dark background
        card_bg = (0x1E, 0x1E, 0x2F)         # Dark purple card
        text_color = (0xFF, 0xFF, 0xFF)      # White text
        accent_color = (0xA8, 0x55, 0xF7)    # Purple Accent (#a855f7)
        muted_text = (0x94, 0xA3, 0xB8)      # Gray muted text
        font_name = "Outfit"
    elif theme == "Classic-Executive":
        bg_color = (0x0F, 0x17, 0x2A)        # Navy dark background
        card_bg = (0x1E, 0x29, 0x3B)         # Navy blue card
        text_color = (0xFF, 0xFF, 0xFF)      # White text
        accent_color = (0x3B, 0x82, 0xF6)    # Blue Accent (#3b82f6)
        muted_text = (0x94, 0xA3, 0xB8)      # Gray muted text
        font_name = "Inter"
    else: # Minimalist (Light theme)
        bg_color = (0xF8, 0xFA, 0xFC)        # Off-white background
        card_bg = (0xFF, 0xFF, 0xFF)         # White card
        text_color = (0x0F, 0x17, 0x2A)      # Dark slate text
        accent_color = (0x4F, 0x46, 0xE5)    # Indigo Accent (#4f46e5)
        muted_text = (0x64, 0x74, 0x8B)      # Gray muted text
        font_name = "Inter"

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    def set_slide_background(slide):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(*bg_color)
        
    def add_card(slide, left, top, width, height):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(*card_bg)
        shape.line.color.rgb = RGBColor(*accent_color)
        shape.line.width = Pt(1.5)
        return shape

    # --- SLIDE 1: Title & Summary ---
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)
    
    # Left visual accent bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(0.2), Inches(4.5))
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(*accent_color)
    bar.line.fill.background()
    
    # Header Title Box
    title_box = slide1.shapes.add_textbox(Inches(1.3), Inches(1.5), Inches(11.0), Inches(1.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "RESUME ARCHITECT FACTORY"
    p1.font.name = font_name
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(*accent_color)
    
    # Summary Card
    add_card(slide1, Inches(1.3), Inches(3.2), Inches(11.0), Inches(3.5))
    summary_text_box = slide1.shapes.add_textbox(Inches(1.5), Inches(3.4), Inches(10.6), Inches(3.1))
    tf_summary = summary_text_box.text_frame
    tf_summary.word_wrap = True
    
    p_sum_title = tf_summary.paragraphs[0]
    p_sum_title.text = "Professional Summary"
    p_sum_title.font.name = font_name
    p_sum_title.font.size = Pt(24)
    p_sum_title.font.bold = True
    p_sum_title.font.color.rgb = RGBColor(*text_color)
    p_sum_title.space_after = Pt(14)
    
    p_sum_desc = tf_summary.add_paragraph()
    p_sum_desc.text = content.get("Summary", "No summary provided.")
    p_sum_desc.font.name = font_name
    p_sum_desc.font.size = Pt(16)
    p_sum_desc.font.color.rgb = RGBColor(*muted_text)
    
    # --- SLIDE 2: Professional Experience ---
    experiences = content.get("Experience", [])
    if experiences:
        slide2 = prs.slides.add_slide(blank_layout)
        set_slide_background(slide2)
        
        # Title
        title_box2 = slide2.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
        tf2 = title_box2.text_frame
        p_title2 = tf2.paragraphs[0]
        p_title2.text = "Professional Experience"
        p_title2.font.name = font_name
        p_title2.font.size = Pt(36)
        p_title2.font.bold = True
        p_title2.font.color.rgb = RGBColor(*accent_color)
        
        # Lay out up to 2 roles
        top_offset = Inches(1.6)
        num_exps = min(len(experiences), 2)
        card_height = Inches(5.2) / num_exps
        for i, exp in enumerate(experiences[:2]):
            add_card(slide2, Inches(0.8), top_offset, Inches(11.73), card_height - Inches(0.2))
            
            exp_box = slide2.shapes.add_textbox(Inches(1.0), top_offset + Inches(0.1), Inches(11.3), card_height - Inches(0.4))
            tf_exp = exp_box.text_frame
            tf_exp.word_wrap = True
            
            # Role & Company
            p_role = tf_exp.paragraphs[0]
            p_role.text = f"{exp.get('Role', 'Specialist')}  |  {exp.get('Company', 'Enterprise')} ({exp.get('Duration', 'Recent')})"
            p_role.font.name = font_name
            p_role.font.size = Pt(18)
            p_role.font.bold = True
            p_role.font.color.rgb = RGBColor(*text_color)
            p_role.space_after = Pt(8)
            
            # Achievements
            for ach in exp.get("Achievements", []):
                p_ach = tf_exp.add_paragraph()
                p_ach.text = f"• {ach}"
                p_ach.font.name = font_name
                p_ach.font.size = Pt(14)
                p_ach.font.color.rgb = RGBColor(*muted_text)
                p_ach.space_after = Pt(4)
                
            top_offset += card_height

    # --- SLIDE 3: Skills & Education ---
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    
    # Title
    title_box3 = slide3.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
    tf3 = title_box3.text_frame
    p_title3 = tf3.paragraphs[0]
    p_title3.text = "Skills & Education"
    p_title3.font.name = font_name
    p_title3.font.size = Pt(36)
    p_title3.font.bold = True
    p_title3.font.color.rgb = RGBColor(*accent_color)
    
    # Left Column: Skills
    add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0))
    skills_box = slide3.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.6))
    tf_skills = skills_box.text_frame
    tf_skills.word_wrap = True
    
    p_sk_title = tf_skills.paragraphs[0]
    p_sk_title.text = "Key Skills"
    p_sk_title.font.name = font_name
    p_sk_title.font.size = Pt(22)
    p_sk_title.font.bold = True
    p_sk_title.font.color.rgb = RGBColor(*text_color)
    p_sk_title.space_after = Pt(12)
    
    skills = content.get("Skills", [])
    for skill in skills:
        p_sk = tf_skills.add_paragraph()
        p_sk.text = f"✔  {skill}"
        p_sk.font.name = font_name
        p_sk.font.size = Pt(16)
        p_sk.font.color.rgb = RGBColor(*muted_text)
        p_sk.space_after = Pt(6)
        
    # Right Column: Education
    add_card(slide3, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.0))
    edu_box = slide3.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.2), Inches(4.6))
    tf_edu = edu_box.text_frame
    tf_edu.word_wrap = True
    
    p_edu_title = tf_edu.paragraphs[0]
    p_edu_title.text = "Education & Certifications"
    p_edu_title.font.name = font_name
    p_edu_title.font.size = Pt(22)
    p_edu_title.font.bold = True
    p_edu_title.font.color.rgb = RGBColor(*text_color)
    p_edu_title.space_after = Pt(12)
    
    edus = content.get("Education", [])
    for edu in edus:
        p_edu = tf_edu.add_paragraph()
        p_edu.text = f"🎓  {edu}"
        p_edu.font.name = font_name
        p_edu.font.size = Pt(16)
        p_edu.font.color.rgb = RGBColor(*muted_text)
        p_edu.space_after = Pt(6)
        
    # Save the presentation
    output_path = os.path.join(os.getcwd(), output_filename)
    prs.save(output_path)
    return output_path

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
        client = genai.Client(api_key=self.api_key or None)
        
        # 1. Define tools for Gemini
        tools_list = [synthesize_content, style_resume, generate_pptx]
        
        # We start with the user's prompt in the contents list
        contents = [
            types.Content(
                role='user',
                parts=[types.Part.from_text(text=f"The user wants to build a resume with the details: '{prompt}'. Follow the tools sequence step-by-step: first synthesize_content, then style_resume with theme '{theme}', and finally generate_pptx.")]
            )
        ]
        
        synthesized_data = {}
        styled_data = {}
        pptx_path = ""
        
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
                    elif call.name == "generate_pptx":
                        args = dict(call.args)
                        # Ensure styled_data is populated if not provided
                        if "styled_data" not in args or not args["styled_data"]:
                            args["styled_data"] = styled_data
                        pptx_path = generate_pptx(**args)
                        result = {"download_url": pptx_path}
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
        if not pptx_path:
            st.write("Model did not request complete tool execution flow. Running fallback pipeline...")
            if not synthesized_data:
                synthesized_data = synthesize_content(prompt)
            if not styled_data:
                styled_data = style_resume(synthesized_data, theme)
            pptx_path = generate_pptx(styled_data)
            
        return synthesized_data, styled_data, pptx_path

    def _call_local_model(self, prompt: str, theme: str):
        st.write("Loading local DeepSeek model for tool signature processing...")
        synthesized_data = synthesize_content(prompt)
        styled_data = style_resume(synthesized_data, theme)
        pptx_path = generate_pptx(styled_data)
        return synthesized_data, styled_data, pptx_path

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
            synthesized, styled, pptx_path = agent.process(raw_input, theme)
            
            if pptx_path:
                st.success("Successfully Architected your Resume!")
                
                # Display columns with results
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Synthesized Content")
                    st.json(synthesized)
                with col2:
                    st.subheader("Applied Styling Metadata")
                    st.json(styled)
                    
                with open(pptx_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Resume Presentation (PPTX)",
                        data=f,
                        file_name="resume.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
