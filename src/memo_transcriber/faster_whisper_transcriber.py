"""
Faster-Whisper transcription backend.
"""

from faster_whisper import WhisperModel
from typing import Optional


# Global model cache to avoid reloading
_faster_whisper_model_cache: dict[str, WhisperModel] = {}


def transcribe_file_faster_whisper(file_path: str, model_size: str = "base") -> str:
    """
    Transcribe an audio file using Faster-Whisper.

    Args:
        file_path: Path to the audio file
        model_size: Model size ('tiny', 'base', 'small', 'medium', 'large-v3')

    Returns:
        Transcribed text or error message
    """
    try:
        # Load model (cached after first load)
        # Use CPU with int8 for efficiency, or "auto" device for GPU if available
        if model_size not in _faster_whisper_model_cache:
            _faster_whisper_model_cache[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )

        model = _faster_whisper_model_cache[model_size]

        # Transcribe - returns segments and info
        segments, info = model.transcribe(file_path, beam_size=5)

        # Collect all segment text
        transcription_parts = []
        for segment in segments:
            transcription_parts.append(segment.text)

        if transcription_parts:
            return " ".join(transcription_parts).strip()

        return "No transcription available"

    except Exception as e:
        return f"Faster-Whisper transcription error: {str(e)}"


def clear_model_cache():
    """Clear the model cache to free memory."""
    global _faster_whisper_model_cache
    _faster_whisper_model_cache.clear()
