import json
import logging
import re
import time
from typing import Any, Optional

import streamlit as st
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

@st.cache_resource(show_spinner=False)
def get_gemini_client(api_key: str) -> genai.Client:
    """Instantiate and cache the Gemini client for the given API key."""
    logger.info("Initialising new Gemini client.")
    return genai.Client(api_key=api_key)

def clean_json_text(raw: str) -> str:
    """Strip markdown fences from LLM output."""
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()

def validate_resume_data(data: dict) -> dict:
    """Ensure all required keys exist with correct types; patch missing values."""
    if not isinstance(data, dict):
        data = {}

    # Contact fields
    for field in ("Name", "Email", "Phone", "LinkedIn", "Location"):
        if not isinstance(data.get(field), str):
            data[field] = ""

    # Summary
    if not isinstance(data.get("Summary"), str) or not data["Summary"].strip():
        data["Summary"] = "Accomplished professional with a proven track record of delivering results."

    # Experience
    if not isinstance(data.get("Experience"), list):
        data["Experience"] = []
    validated_exp: list[dict] = []
    for exp in data["Experience"]:
        if not isinstance(exp, dict):
            continue
        validated_exp.append({
            "Role": str(exp.get("Role", "Professional")),
            "Company": str(exp.get("Company", "Organisation")),
            "Duration": str(exp.get("Duration", "")),
            "Achievements": [str(a) for a in exp.get("Achievements", []) if a],
        })
    data["Experience"] = validated_exp

    # Skills / Education
    for key in ("Skills", "Education"):
        if not isinstance(data.get(key), list):
            data[key] = []
        data[key] = [str(v) for v in data[key] if v]

    return data

def call_gemini_with_retry(
    client: genai.Client,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    status_ph: Any,
    step_label: str,
    use_schema: bool = False,
) -> Optional[str]:
    """Call Gemini with retry logic. Returns raw response text or None."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("%s — attempt %d/%d", step_label, attempt, MAX_RETRIES)
            status_ph.info(f"🔄 {step_label} — attempt {attempt}/{MAX_RETRIES}…")

            config_kwargs: dict = {
                "system_instruction": system_prompt,
                "temperature": temperature,
            }
            if use_schema:
                config_kwargs["response_mime_type"] = "application/json"
                config_kwargs["response_schema"] = RESUME_SCHEMA
            else:
                config_kwargs["response_mime_type"] = "application/json"

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )

            if response and response.text:
                logger.info("%s — success on attempt %d", step_label, attempt)
                return response.text

            status_ph.warning(f"⚠️ {step_label} — empty response. Retrying…")

        except Exception as exc:
            msg = str(exc).lower()
            logger.error("%s — error: %s", step_label, exc)

            if any(k in msg for k in ("api key", "api_key", "permission denied", "invalid_api_key")):
                st.error("🔑 **Invalid API Key.** Please check your Gemini API key in the sidebar.")
                return None
            if any(k in msg for k in ("quota", "resource_exhausted", "429")):
                st.error("📊 **Quota exceeded.** Please wait or check your Gemini plan.")
                return None
            if any(k in msg for k in ("timeout", "deadline")):
                status_ph.warning(f"⏱️ {step_label} — timeout on attempt {attempt}. Retrying…")
            elif any(k in msg for k in ("network", "connection", "unavailable")):
                status_ph.warning(f"🌐 {step_label} — network error on attempt {attempt}. Retrying…")
            else:
                status_ph.warning(f"⚠️ {step_label} — {exc}. Retrying…")

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS * attempt)

    st.error(f"❌ {step_label} failed after {MAX_RETRIES} attempts.")
    return None

def run_extraction_pass(
    client: genai.Client,
    raw_input: str,
    status_ph: Any,
) -> Optional[dict]:
    """Pass 1: Extract structured resume data using Gemini structured output."""
    raw = call_gemini_with_retry(
        client, PASS1_SYSTEM_PROMPT,
        PASS1_USER_TEMPLATE.format(raw_input=raw_input),
        temperature=0.3,
        status_ph=status_ph,
        step_label="Pass 1 — Extracting structured content",
        use_schema=True,
    )
    if raw is None:
        return None
    try:
        parsed = json.loads(clean_json_text(raw))
        logger.info("Pass 1 parsed successfully.")
        return validate_resume_data(parsed)
    except json.JSONDecodeError as exc:
        logger.error("Pass 1 JSON decode error: %s", exc)
        st.error("❌ Pass 1 returned invalid JSON. Please try again.")
        return None

def run_enhancement_pass(
    client: genai.Client,
    extracted: dict,
    status_ph: Any,
) -> dict:
    """Pass 2: Enhance writing quality whilst preserving schema."""
    raw = call_gemini_with_retry(
        client, PASS2_SYSTEM_PROMPT,
        PASS2_USER_TEMPLATE.format(input_json=json.dumps(extracted, indent=2)),
        temperature=0.2,
        status_ph=status_ph,
        step_label="Pass 2 — Enhancing executive language",
        use_schema=True,
    )
    if raw is None:
        logger.warning("Pass 2 failed — falling back to Pass 1 output.")
        return extracted
    try:
        parsed = json.loads(clean_json_text(raw))
        logger.info("Pass 2 parsed successfully.")
        return validate_resume_data(parsed)
    except json.JSONDecodeError:
        logger.warning("Pass 2 invalid JSON — using Pass 1 output.")
        st.warning("⚠️ Pass 2 returned invalid JSON — using Pass 1 output.")
        return extracted
