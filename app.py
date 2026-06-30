import os
import json
import requests
from google import genai
from google.genai import types

# Define Tool Registry actions
def synthesize_content(raw_input: str) -> dict:
    """Extracts key achievements from raw user input and maps them to standard resume sections."""
    print("[Tool: synthesize_content] Extracting achievements...")
    # Real implementations would process content or delegate parsing.
    # Here is a mock response showing standard structure:
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
    print(f"[Tool: style_resume] Applying theme: {theme}...")
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
    print("[Tool: generate_pdf] Calling Nutrient DWS API...")
    # In a real setup, we would perform a post request to the Nutrient DWS API.
    # We will output a mock status/download link.
    download_url = f"https://api.nutrient.dws/download/{output_filename}"
    print(f"[Tool: generate_pdf] Finished! Download at: {download_url}")
    return download_url

# Tool Registry for dynamic invocation
tools = [
    {
        "name": "synthesize_content",
        "description": "Extracts and categorizes career history.",
        "function": synthesize_content
    },
    {
        "name": "style_resume",
        "description": "Applies layout/theme to structured resume data.",
        "function": style_resume
    },
    {
        "name": "generate_pdf",
        "description": "Converts resume data to PDF using Nutrient DWS API.",
        "function": generate_pdf
    }
]

class ResumeArchitect:
    def __init__(self, provider: str):
        self.provider = provider.lower()
        
    def process(self, prompt: str):
        print(f"Routing process via provider: '{self.provider}'")
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "huggingface":
            return self._call_local_model(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_gemini(self, prompt: str):
        print("Using google-genai SDK for tool calling...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment. Initializing default client...")
        
        # Initialize Google GenAI client
        client = genai.Client()
        
        # In a full flow, we pass the tools to the model:
        # response = client.models.generate_content(
        #     model='gemini-2.5-flash',
        #     contents=prompt,
        #     config=types.GenerateContentConfig(
        #         tools=[synthesize_content, style_resume, generate_pdf]
        #     )
        # )
        # Below we mock/run the sequencing logic:
        print(f"Mocking Gemini response/tool execution for prompt: '{prompt}'")
        synthesized = synthesize_content(prompt)
        styled = style_resume(synthesized, "Modern-Tech")
        pdf_url = generate_pdf(styled)
        return pdf_url

    def _call_local_model(self, prompt: str):
        print("Loading local Hugging Face model for tool call synthesis...")
        # DeepSeek-R1-Distill-1.5B local processing logic:
        # from transformers import AutoModelForCausalLM, AutoTokenizer
        # tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-1.5B")
        # model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-1.5B")
        
        # Process the tool signatures and return result:
        print("Local model processed prompt & invoked the tool sequence.")
        synthesized = synthesize_content(prompt)
        styled = style_resume(synthesized, "Modern-Tech")
        pdf_url = generate_pdf(styled)
        return pdf_url

# Launch Setup
if __name__ == "__main__":
    import sys
    
    # Toggle provider via RESUME_PROVIDER environment variable
    PROVIDER = os.getenv("RESUME_PROVIDER", "gemini")
    agent = ResumeArchitect(provider=PROVIDER)
    
    # Sample run
    sample_prompt = "Built a dynamic Gold Standard Dashboard in Python and Streamlit."
    if len(sys.argv) > 1:
        sample_prompt = " ".join(sys.argv[1:])
        
    result_url = agent.process(sample_prompt)
    print(f"Resulting PDF Link: {result_url}")
