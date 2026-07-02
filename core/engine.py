import json
import logging
import time
from typing import Any, Optional

from google import genai
from google.genai import types

from core.prompts import (
    GEMINI_MODEL,
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    RESUME_SCHEMA,
    PASS1_SYSTEM_PROMPT,
    PASS1_USER_TEMPLATE,
    PASS2_SYSTEM_PROMPT,
    PASS2_USER_TEMPLATE,
)

logger = logging.getLogger("resume_architect")

def get_gemini_client(api_key: str) -> genai.Client:
    """Initialise and return the Gemini API client."""
    return genai.Client(api_key=api_key)

def call_gemini_with_retry(
    client: genai.Client,
    prompt: str,
    system_instruction: str,
    tools: Optional[list] = None,
    response_schema: Optional[types.Schema] = None,
    status_ph: Any = None,
) -> Optional[str]:
    """Execute a Gemini API call with exponential backoff and structured output support."""
    config_kwargs = {
        "system_instruction": system_instruction,
        "temperature": 0.3,
    }
    if tools:
        config_kwargs["tools"] = tools
    if response_schema:
        config_kwargs["response_mime_type"] = "application/json"
        config_kwargs["response_schema"] = response_schema

    config = types.GenerateContentConfig(**config_kwargs)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Calling Gemini API (Attempt %d/%d)...", attempt, MAX_RETRIES)
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as exc:
            logger.warning("Attempt %d failed: %s", attempt, exc)
            if status_ph:
                status_ph.warning(f"API attempt {attempt} failed. Retrying...")
            if attempt == MAX_RETRIES:
                logger.error("All Gemini API attempts failed.")
                if status_ph:
                    status_ph.error(f"❌ API Error: {exc}")
                return None
            time.sleep(RETRY_DELAY_SECONDS ** attempt)
    return None

def run_research_pass(
    client: genai.Client,
    target_roles: list[str],
    status_ph: Any,
    selected_stream: str = "BSc Computer Science / IT",
) -> str:
    """Pass 0: Use Google Search to find the best free courses/certifications for the target roles."""
    roles_str = ", ".join(target_roles)
    contents = (
        f"The user is a {selected_stream} student aiming to become one of the following in 2-3 years: {roles_str}.\n\n"
        "Search the web for the absolute best, highly-recognized FREE or open-source online courses, bootcamps, and certifications "
        "(e.g., from freeCodeCamp, Harvard CS50, AWS Educate, Google Cloud Skill Boost, DeepLearning.AI via financial aid, OSSU) "
        "that are mandatory or highly recommended for these specific roles. Summarize the best 3-5 free courses they should take."
    )
    
    tools = [types.Tool(google_search=types.GoogleSearch())]
    
    result = call_gemini_with_retry(
        client=client,
        prompt=contents,
        system_instruction="You are a career research assistant using Google Search to find high-value FREE tech courses.",
        tools=tools,
        status_ph=status_ph
    )
    return result or "No research data found."

def run_extraction_pass(
    client: genai.Client,
    target_roles: list[str],
    research_summary: str,
    status_ph: Any,
    selected_stream: str = "BSc Computer Science / IT",
    degree_placeholder: str = "Bachelor of Science in Computer Science",
) -> Optional[dict]:
    """Pass 1: Generate the Future Resume JSON based on selected roles and free course research."""
    prompt = PASS1_USER_TEMPLATE.format(
        research_summary=research_summary,
        target_roles=", ".join(target_roles)
    )

    system_instruction = PASS1_SYSTEM_PROMPT.replace(
        "BSc Computer Science", selected_stream
    ).replace(
        "Bachelor of Science in Computer Science", degree_placeholder
    )

    result_text = call_gemini_with_retry(
        client=client,
        prompt=prompt,
        system_instruction=system_instruction,
        response_schema=RESUME_SCHEMA,
        status_ph=status_ph
    )
    
    if not result_text:
        return None
        
    try:
        return json.loads(result_text)
    except json.JSONDecodeError as exc:
        logger.error("Pass 1 JSON parse failed: %s", exc)
        if status_ph:
            status_ph.error("❌ Failed to parse AI output (Pass 1).")
        return None

def run_enhancement_pass(
    client: genai.Client,
    extracted_data: dict,
    status_ph: Any,
) -> dict:
    """Pass 2: Elevate the generated future resume to an elite standard."""
    input_json = json.dumps(extracted_data, indent=2)
    prompt = PASS2_USER_TEMPLATE.format(input_json=input_json)
    
    result_text = call_gemini_with_retry(
        client=client,
        prompt=prompt,
        system_instruction=PASS2_SYSTEM_PROMPT,
        response_schema=RESUME_SCHEMA,
        status_ph=status_ph
    )
    
    if not result_text:
        logger.warning("Pass 2 failed, falling back to Pass 1 data.")
        return extracted_data
        
    try:
        return json.loads(result_text)
    except json.JSONDecodeError as exc:
        logger.error("Pass 2 JSON parse failed: %s", exc)
        return extracted_data
