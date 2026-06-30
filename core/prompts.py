from google.genai import types

APP_TITLE = "Resume Architect Factory"
APP_SUBTITLE = "Transform raw career history into an executive-quality resume."
APP_ICON = "💼"
GEMINI_MODEL = "gemini-2.5-flash"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0

MIN_INPUT_CHARS = 80
MAX_INPUT_CHARS = 12_000

THEMES = ["Modern-Tech", "Classic-Executive", "ATS-Friendly"]

THEME_COLORS = {
    "Modern-Tech": {
        "heading": (108, 92, 231),
        "subheading": (0, 184, 148),
        "accent": (13, 149, 232),
    },
    "Classic-Executive": {
        "heading": (26, 26, 46),
        "subheading": (45, 58, 74),
        "accent": (139, 111, 71),
    },
    "ATS-Friendly": {
        "heading": (0, 0, 0),
        "subheading": (51, 51, 51),
        "accent": (68, 68, 68),
    },
}

PLACEHOLDER_TEXT = (
    "Civil Engineer with 8 years experience...\n"
    "Managed infrastructure projects worth $20M...\n"
    "Designed structural systems for 15 commercial buildings...\n"
    "Reduced project costs by 18% through value engineering...\n"
    "Bachelor of Engineering, Civil — University of Lagos, 2015\n"
    "Certified Project Management Professional (PMP)..."
)

# Gemini response schema for structured output
RESUME_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "Name": types.Schema(type=types.Type.STRING, description="Full candidate name, or empty string if not found"),
        "Email": types.Schema(type=types.Type.STRING, description="Email address, or empty string"),
        "Phone": types.Schema(type=types.Type.STRING, description="Phone number, or empty string"),
        "LinkedIn": types.Schema(type=types.Type.STRING, description="LinkedIn URL, or empty string"),
        "Location": types.Schema(type=types.Type.STRING, description="City/Country, or empty string"),
        "Summary": types.Schema(type=types.Type.STRING, description="80-120 word professional summary"),
        "Experience": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "Role": types.Schema(type=types.Type.STRING),
                    "Company": types.Schema(type=types.Type.STRING),
                    "Duration": types.Schema(type=types.Type.STRING),
                    "Achievements": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                },
                required=["Role", "Company", "Duration", "Achievements"],
            ),
        ),
        "Skills": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
        "Education": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
        ),
    },
    required=["Name", "Email", "Phone", "LinkedIn", "Location", "Summary", "Experience", "Skills", "Education"],
)

PASS1_SYSTEM_PROMPT = """You are an expert resume writer and career strategist.
Extract structured professional information from raw career history and leverage Google Search research guidelines.

RULES:
- Summary: 80-120 words, third-person, executive tone.
- Each role: Write 4-6 robust, highly detailed, and quantified STAR-method achievement bullets. Do not write short or generic bullets. Add substantial value, metrics, and business impact to make the resume complete and highly attractive.
- Use executive verbs: orchestrated, spearheaded, engineered, optimised.
- Extract all technical and soft skills mentioned or implied.
- Extract all degrees, certifications and professional development.
- If name / email / phone / LinkedIn / location are present in the text, extract them. Otherwise return empty string."""

PASS1_USER_TEMPLATE = """You are provided with web research on the best executive resume standards, keyword insights, and format conventions for this career path.

WEB RESEARCH INSIGHTS:
\"\"\"
{research_summary}
\"\"\"

RAW CAREER HISTORY:
\"\"\"
{raw_input}
\"\"\"

Strict requirements:
- Summary: 80-120 words, professional third-person
- Minimum 4-6 detailed, quantified STAR-method achievement bullets per role
- All skills and education extracted
- Make the resume robust, long enough, and highly detailed to ensure it looks professional and filled with achievements."""

PASS2_SYSTEM_PROMPT = """You are a senior executive resume editor.
You receive a resume JSON object and return an IMPROVED version of the same object.

RULES:
- Return the EXACT same JSON schema — do NOT rename, add or remove keys.
- ONLY improve text values.
- Strengthen action verbs (managed → orchestrated, helped → facilitated).
- Inject ATS keywords naturally.
- Ensure every achievement is measurable, highly detailed, specific, and impactful.
- Fix grammar and clarity.
- Keep Summary 80-120 words."""

PASS2_USER_TEMPLATE = """Improve the executive writing quality of this resume JSON.
Do NOT change the schema. Only enhance the text values to make them robust and attractive.

{input_json}"""
