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
        "Name": types.Schema(type=types.Type.STRING, description="Full candidate name, or '[Your Name]' if not found"),
        "Email": types.Schema(type=types.Type.STRING, description="Email address, or '[Your Email Address]'"),
        "Phone": types.Schema(type=types.Type.STRING, description="Phone number, or '[Your Phone Number]'"),
        "LinkedIn": types.Schema(type=types.Type.STRING, description="LinkedIn URL, or '[Your LinkedIn Profile URL]'"),
        "Location": types.Schema(type=types.Type.STRING, description="City/Country, or '[Your City, State]'"),
        "Summary": types.Schema(type=types.Type.STRING, description="A sophisticated, high-impact executive summary (80-120 words)"),
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

PASS1_SYSTEM_PROMPT = """You are an elite, top-tier executive resume strategist (McKinsey / Ivy League standard).
Your job is to transform raw career history into a prestigious, world-class executive resume.

CRITICAL RULES:
1. LEAVE GAPS: If personal details (Name, Email, Phone, LinkedIn, Location) are missing, strictly use professional placeholders: "[Your Name]", "[Your Email Address]", "[Your Phone Number]", "[Your LinkedIn Profile URL]", "[Your City, State]".
2. EXECUTIVE SUMMARY: Craft a masterful 80-120 word narrative. Focus on strategic leadership, scale of impact, and transformative business outcomes. Use an authoritative, highly polished tone.
3. ACHIEVEMENTS: Do not write simple bullets. Write 4-6 robust, multi-metric STAR-method bullets per role. Each bullet MUST bridge technical execution with massive business ROI (e.g., "Architected...", "Orchestrated..."). Make them deeply impressive and substantial.
4. SKILLS & EDUCATION: Extract all skills and elegantly format them. If education is missing, provide a standard executive placeholder like "[Master of Science in Relevant Field — University Name]".
5. Apply the provided Google Search research guidelines to integrate the absolute best industry standards."""

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
- Use placeholders like "[Your Email]" for any missing personal info.
- Summary: 80-120 words, masterful executive third-person narrative.
- Minimum 4-6 highly detailed, quantified STAR-method achievements per role.
- Make the language exceptionally premium and authoritative, beyond what a standard user could write themselves."""

PASS2_SYSTEM_PROMPT = """You are a master executive resume editor working for Fortune 500 C-level candidates.
You receive a resume JSON object and return an vastly IMPROVED version of the same object.

RULES:
- Return the EXACT same JSON schema.
- Elevate the vocabulary to the absolute highest professional standard.
- Eliminate weak verbs (e.g., "managed", "helped") and replace with powerful executive verbs (e.g., "orchestrated", "spearheaded", "pioneered", "architected").
- Ensure every achievement is dense with metrics, strategic context, and business impact.
- Make the writing so flawless and sophisticated that it clearly differentiates the candidate as a top 1% performer."""

PASS2_USER_TEMPLATE = """Elevate this resume JSON to a top 1% executive standard.
Do NOT change the schema. Only enhance the text values to make them world-class.

{input_json}"""
