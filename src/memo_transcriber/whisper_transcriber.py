"""
OpenAI Whisper transcription backend.
"""

import whisper
from typing import Optional


# Global model cache to avoid reloading
_whisper_model_cache: dict[str, whisper.Whisper] = {}


def transcribe_file_whisper(file_path: str, model_size: str = "base") -> str:
    """
    Transcribe an audio file using OpenAI Whisper.

    Args:
        file_path: Path to the audio file
        model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')

    Returns:
        Transcribed text or error message
    """
    try:
        # Load model (cached after first load)
        if model_size not in _whisper_model_cache:
            _whisper_model_cache[model_size] = whisper.load_model(model_size)

        model = _whisper_model_cache[model_size]

        # Transcribe
        result = model.transcribe(file_path)

        if result and "text" in result:
            return result["text"].strip()

        return "No transcription available"

    except Exception as e:
        return f"Whisper transcription error: {str(e)}"


def clear_model_cache():
    """Clear the model cache to free memory."""
    global _whisper_model_cache
    _whisper_model_cache.clear()
