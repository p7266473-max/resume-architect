from google.genai import types

APP_TITLE = "Future Resume Architect"
APP_SUBTITLE = "Design your career path. Generate the elite resume you'll have in 3 years."
APP_ICON = "🚀"
GEMINI_MODEL = "gemini-2.5-flash"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2.0

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

CAREER_OPTIONS = [
    "Software Engineer (Backend)",
    "Software Engineer (Frontend)",
    "Full Stack Developer",
    "Data Scientist / ML Engineer",
    "Data Analyst",
    "Cloud Architect / Cloud Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst",
    "Mobile App Developer (iOS/Android)",
    "Game Developer",
    "Product Manager",
    "Tech Entrepreneur / Founder",
    "Blockchain Developer",
    "UI/UX Designer (Tech-focused)"
]

# Gemini response schema for structured output
RESUME_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "Name": types.Schema(type=types.Type.STRING, description="Full candidate name, or '[Your Name]' if not found"),
        "Email": types.Schema(type=types.Type.STRING, description="Email address, or '[Your Email Address]'"),
        "Phone": types.Schema(type=types.Type.STRING, description="Phone number, or '[Your Phone Number]'"),
        "LinkedIn": types.Schema(type=types.Type.STRING, description="LinkedIn URL, or '[Your LinkedIn Profile URL]'"),
        "Location": types.Schema(type=types.Type.STRING, description="City/Country, or '[Your City, State]'"),
        "Summary": types.Schema(type=types.Type.STRING, description="A highly ambitious, forward-looking summary of a recent BSc Computer Science grad."),
        "Experience": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "Role": types.Schema(type=types.Type.STRING, description="Future Job Title or Internship"),
                    "Company": types.Schema(type=types.Type.STRING, description="Placeholder like '[Target Tech Company]' or '[Insert Startup Name]'"),
                    "Duration": types.Schema(type=types.Type.STRING, description="e.g. '2027 - Present'"),
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

PASS1_SYSTEM_PROMPT = """You are a "Future Career Architect". 
Your user is currently a BSc Computer Science student. They have selected up to 3 target roles they want to achieve in the next 2-3 years.
Your job is to generate their FUTURE resume—the exact elite resume they will have 3 years from now.

CRITICAL RULES:
1. EDUCATION: Must include "Bachelor of Science in Computer Science - [Insert University Name]". Leave gaps/placeholders for their actual university.
2. CERTIFICATIONS: Based on the web research provided, list 3 to 4 REAL, highly-regarded FREE or Open-Source courses/certifications (e.g. freeCodeCamp, CS50, AWS Educate, Google Cloud Skill Boost) that they MUST take in the next 2 years to achieve their goals. Present them as if they have already completed them in the future.
3. EXPERIENCE: Generate 2 to 3 highly impressive future internships or personal projects they will have completed. Leave the company names as blanks (e.g., "[Target Tech Company]", "[Open Source Project]"). Make the achievements incredibly impressive and quantifiable.
4. PERSONAL DETAILS: Use placeholders like "[Your Name]", "[Your Email]".
5. TONE: Ambitious, highly competent recent graduate ready for top-tier tech roles."""

PASS1_USER_TEMPLATE = """You are provided with web research on the best free/open-source certifications and courses for the user's target roles.

WEB RESEARCH INSIGHTS (FREE COURSES):
\"\"\"
{research_summary}
\"\"\"

TARGET FUTURE ROLES:
\"\"\"
{target_roles}
\"\"\"

Generate the complete FUTURE resume json based on the guidelines. Ensure the Education section prominently features their BSc in Computer Science and the exact free certifications from the research."""

PASS2_SYSTEM_PROMPT = """You are an elite resume editor.
You receive a JSON object of a 'future resume' for a BSc Computer Science student aiming for top tech roles.

RULES:
- Return the EXACT same JSON schema.
- Elevate the vocabulary to a highly professional, ambitious standard.
- Ensure the 'Experience' achievements read like a top-tier candidate (using action verbs like 'Architected', 'Developed', 'Optimized').
- Keep the placeholders (like [Target Tech Company], [Insert University Name]) completely intact.
- Make the 'Summary' captivating and ambitious."""

PASS2_USER_TEMPLATE = """Elevate this future resume JSON to a top 1% standard.
Do NOT change the schema. Keep placeholders. Only enhance the text values.

{input_json}"""
