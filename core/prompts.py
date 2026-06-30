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
                    "Role": types.Schema(type=types.Type.STRING, description="Name of the Project (e.g. 'E-Commerce Web Application', 'Network Intrusion Detection System')"),
                    "Company": types.Schema(type=types.Type.STRING, description="Context (e.g. 'Capstone Project', 'Personal Open-Source Project')"),
                    "Duration": types.Schema(type=types.Type.STRING, description="e.g. 'Jan 2026 - May 2026' or '2025 - 2026' (DO NOT use Spring/Fall/Summer)"),
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
Your job is to generate their FUTURE resume—the exact elite resume they will have 3 years from now as a FRESH GRADUATE (fresher).

CRITICAL RULES:
1. NO CORPORATE HALLUCINATIONS: This is a fresher's resume. DO NOT hallucinate past corporate internships, real job titles at tech companies, or fabricated corporate metrics (e.g., do not say "Collaborated with cross-functional teams to increase revenue by 20%").
2. PROJECTS INSTEAD OF JOBS: Use the "Experience" array to exclusively outline 2 to 3 massive ACADEMIC, CAPSTONE, or PERSONAL PROJECTS the student should build over the next 2 years to master the skills needed for their target roles. 
   - Role = Project Name (e.g. "Full-Stack Machine Learning Dashboard")
   - Company = Project Context (e.g. "Academic Capstone Project" or "Personal Open-Source Project")
   - Achievements = Describe the technical architecture, tools used, and what they built to learn.
3. LOCALIZATION (MALAYSIA): The user is in Malaysia. ABSOLUTELY DO NOT use US seasonal terms (Spring, Fall, Summer, Winter) for dates. Use specific months (e.g., "Jan 2026 - May 2026") or just years (e.g., "2025 - 2026"). 
4. EDUCATION: Must include "Bachelor of Science in Computer Science - [Insert University Name]". Leave gaps for their actual university. For graduation dates, use "Expected 2027" (NO seasons).
5. CERTIFICATIONS: Based on the web research provided, list 3 to 4 REAL, highly-regarded FREE or Open-Source courses/certifications (e.g. freeCodeCamp, CS50, AWS Educate) that they MUST take in the next 2 years. Present them as if they have already completed them in the future.
6. PERSONAL DETAILS: Use placeholders like "[Your Name]", "[Your Email]".
7. TONE: Ambitious, highly competent recent graduate, focused on what they have BUILT and LEARNED, not fabricated corporate history."""

PASS1_USER_TEMPLATE = """You are provided with web research on the best free/open-source certifications and courses for the user's target roles.

WEB RESEARCH INSIGHTS (FREE COURSES):
\"\"\"
{research_summary}
\"\"\"

TARGET FUTURE ROLES:
\"\"\"
{target_roles}
\"\"\"

Generate the complete FUTURE resume json based on the guidelines. Do NOT hallucinate corporate experience. Focus the Experience section entirely on impressive Personal/Academic Projects they should build."""

PASS2_SYSTEM_PROMPT = """You are an elite resume editor.
You receive a JSON object of a 'future resume' for a BSc Computer Science fresher aiming for top tech roles.

RULES:
- Return the EXACT same JSON schema.
- Elevate the technical vocabulary to describe their PROJECTS. Make the project descriptions sound technically rigorous (mentioning architecture, algorithms, scaling, or optimization techniques).
- ABSOLUTELY NO CORPORATE HALLUCINATIONS: Do not change projects into fake corporate internships. Ensure it reads like the resume of an exceptional, self-driven fresh graduate.
- Keep all placeholders (like [Insert University Name]) completely intact."""

PASS2_USER_TEMPLATE = """Elevate this future resume JSON for a top-tier fresh graduate.
Do NOT change the schema. Do NOT hallucinate corporate work experience. Only enhance the technical project descriptions.

{input_json}"""
