import os

from django.core.exceptions import ImproperlyConfigured

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_NAME = os.getenv("ELEVENLABS_VOICE_NAME", "alloy")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v1")

try:
    from elevenlabs import set_api_key, generate
except ImportError:
    set_api_key = None
    generate = None


def is_tts_enabled() -> bool:
    return bool(ELEVENLABS_API_KEY) and generate is not None


def generate_speech(text: str) -> bytes:
    if not is_tts_enabled():
        raise ImproperlyConfigured(
            "ElevenLabs TTS is not configured or the elevenlabs package is missing. "
            "Set ELEVENLABS_API_KEY and install elevenlabs."
        )

    set_api_key(ELEVENLABS_API_KEY)

    audio_bytes = generate(
        text=text,
        voice=ELEVENLABS_VOICE_NAME,
        model=ELEVENLABS_MODEL,
    )

    if isinstance(audio_bytes, bytes):
        return audio_bytes

    try:
        return audio_bytes.content
    except Exception:
        raise RuntimeError("Unexpected response from ElevenLabs TTS service.")
