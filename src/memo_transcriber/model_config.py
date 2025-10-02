"""
Model configuration for transcription engines.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class TranscriptionModel(str, Enum):
    """Available transcription models."""
    APPLE_SPEECH = "apple"
    WHISPER_TINY = "whisper-tiny"
    WHISPER_BASE = "whisper-base"
    WHISPER_SMALL = "whisper-small"
    WHISPER_MEDIUM = "whisper-medium"
    WHISPER_LARGE = "whisper-large"
    FASTER_WHISPER_TINY = "faster-whisper-tiny"
    FASTER_WHISPER_BASE = "faster-whisper-base"
    FASTER_WHISPER_SMALL = "faster-whisper-small"
    FASTER_WHISPER_MEDIUM = "faster-whisper-medium"
    FASTER_WHISPER_LARGE = "faster-whisper-large-v3"


@dataclass
class ModelInfo:
    """Information about a transcription model."""
    name: str
    display_name: str
    engine: str  # 'apple', 'whisper', 'faster-whisper'
    model_size: Optional[str]  # 'tiny', 'base', 'small', 'medium', 'large'
    description: str
    requires_internet: bool = False
    relative_speed: str = "medium"  # 'very-fast', 'fast', 'medium', 'slow', 'very-slow'
    relative_accuracy: str = "medium"  # 'low', 'medium', 'high', 'very-high'


MODEL_INFO = {
    TranscriptionModel.APPLE_SPEECH: ModelInfo(
        name="apple",
        display_name="Apple Speech Recognition",
        engine="apple",
        model_size=None,
        description="macOS native speech recognition (fast, no downloads)",
        requires_internet=False,
        relative_speed="very-fast",
        relative_accuracy="medium"
    ),
    TranscriptionModel.WHISPER_TINY: ModelInfo(
        name="whisper-tiny",
        display_name="Whisper Tiny",
        engine="whisper",
        model_size="tiny",
        description="Fastest Whisper model, ~75MB (lower accuracy)",
        relative_speed="fast",
        relative_accuracy="medium"
    ),
    TranscriptionModel.WHISPER_BASE: ModelInfo(
        name="whisper-base",
        display_name="Whisper Base",
        engine="whisper",
        model_size="base",
        description="Fast Whisper model, ~142MB (good balance)",
        relative_speed="medium",
        relative_accuracy="high"
    ),
    TranscriptionModel.WHISPER_SMALL: ModelInfo(
        name="whisper-small",
        display_name="Whisper Small",
        engine="whisper",
        model_size="small",
        description="Accurate Whisper model, ~466MB",
        relative_speed="medium",
        relative_accuracy="high"
    ),
    TranscriptionModel.WHISPER_MEDIUM: ModelInfo(
        name="whisper-medium",
        display_name="Whisper Medium",
        engine="whisper",
        model_size="medium",
        description="High accuracy Whisper model, ~1.5GB (slower)",
        relative_speed="slow",
        relative_accuracy="very-high"
    ),
    TranscriptionModel.WHISPER_LARGE: ModelInfo(
        name="whisper-large",
        display_name="Whisper Large",
        engine="whisper",
        model_size="large",
        description="Best accuracy Whisper model, ~3GB (slowest)",
        relative_speed="very-slow",
        relative_accuracy="very-high"
    ),
    TranscriptionModel.FASTER_WHISPER_TINY: ModelInfo(
        name="faster-whisper-tiny",
        display_name="Faster-Whisper Tiny",
        engine="faster-whisper",
        model_size="tiny",
        description="4x faster than Whisper Tiny, same accuracy",
        relative_speed="very-fast",
        relative_accuracy="medium"
    ),
    TranscriptionModel.FASTER_WHISPER_BASE: ModelInfo(
        name="faster-whisper-base",
        display_name="Faster-Whisper Base",
        engine="faster-whisper",
        model_size="base",
        description="4x faster than Whisper Base, same accuracy (recommended)",
        relative_speed="fast",
        relative_accuracy="high"
    ),
    TranscriptionModel.FASTER_WHISPER_SMALL: ModelInfo(
        name="faster-whisper-small",
        display_name="Faster-Whisper Small",
        engine="faster-whisper",
        model_size="small",
        description="4x faster than Whisper Small, same accuracy",
        relative_speed="fast",
        relative_accuracy="high"
    ),
    TranscriptionModel.FASTER_WHISPER_MEDIUM: ModelInfo(
        name="faster-whisper-medium",
        display_name="Faster-Whisper Medium",
        engine="faster-whisper",
        model_size="medium",
        description="4x faster than Whisper Medium, same accuracy",
        relative_speed="medium",
        relative_accuracy="very-high"
    ),
    TranscriptionModel.FASTER_WHISPER_LARGE: ModelInfo(
        name="faster-whisper-large-v3",
        display_name="Faster-Whisper Large v3",
        engine="faster-whisper",
        model_size="large-v3",
        description="4x faster than Whisper Large, best accuracy",
        relative_speed="slow",
        relative_accuracy="very-high"
    ),
}


def get_model_info(model: TranscriptionModel) -> ModelInfo:
    """Get information about a specific model."""
    return MODEL_INFO[model]


def list_available_models() -> list[tuple[str, str]]:
    """List all available models with their display names."""
    return [(model.value, info.display_name) for model, info in MODEL_INFO.items()]


def get_default_model() -> TranscriptionModel:
    """Get the default transcription model."""
    return TranscriptionModel.FASTER_WHISPER_BASE
