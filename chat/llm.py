import os
from typing import List, Dict

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-1.5-pro")

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def is_llm_enabled() -> bool:
    if LLM_PROVIDER == "openai":
        return openai is not None and bool(OPENAI_API_KEY)
    elif LLM_PROVIDER == "gemini":
        return genai is not None and bool(GOOGLE_API_KEY)
    return False


def _ensure_provider():
    if LLM_PROVIDER == "openai":
        if openai is None:
            raise RuntimeError("OpenAI SDK is not installed. Install it with `pip install openai`.")
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured.")
        openai.api_key = OPENAI_API_KEY
    elif LLM_PROVIDER == "gemini":
        if genai is None:
            raise RuntimeError("Google Generative AI SDK is not installed. Install it with `pip install google-generativeai`.")
        if not GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not configured.")
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        raise RuntimeError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def generate_llm_response(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 420) -> str:
    _ensure_provider()

    if LLM_PROVIDER == "openai":
        completion = openai.ChatCompletion.create(
            model=OPENAI_CHAT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return completion.choices[0].message.content.strip()

    if LLM_PROVIDER == "gemini":
        response = genai.ChatCompletion.create(
            model=GEMINI_CHAT_MODEL,
            messages=messages,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return response.last

    raise RuntimeError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
