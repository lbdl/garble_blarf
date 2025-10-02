import Speech
import time
import Foundation
from .model_config import TranscriptionModel, get_model_info


def transcribe_file_apple_speech(file_path: str) -> str:
    """Transcribe using Apple Speech Recognition framework."""
    try:
        recogniser = Speech.SFSpeechRecognizer.alloc().init()

        if not recogniser.isAvailable():
            return "Speech recognition not available"

        url = Foundation.NSURL.fileURLWithPath_(file_path)

        # Create recognition request
        request = Speech.SFSpeechURLRecognitionRequest.alloc().initWithURL_(url)
        request.setShouldReportPartialResults_(False)

        # Result storage
        result_text = {"text": "", "finished": False, "error": None}

        def completion_handler(result, error):
            if error:
                result_text["error"] = str(error)
            elif result and result.isFinal():
                result_text["text"] = result.bestTranscription().formattedString()
            result_text["finished"] = True

        # Start recognition
        task = recogniser.recognitionTaskWithRequest_resultHandler_(
            request, completion_handler
        )

        # Wait for completion
        timeout = 60
        start_time = time.time()

        while not result_text["finished"] and (time.time() - start_time) < timeout:
            Foundation.NSRunLoop.currentRunLoop().runUntilDate_(
                Foundation.NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )

        if result_text["error"]:
            return f"Recognition failed: {result_text['error']}"

        return result_text["text"] or "No transcription available"

    except Exception as e:
        return f"Transcription error: {str(e)}"


def transcribe_file(file_path: str, model: TranscriptionModel = TranscriptionModel.APPLE_SPEECH) -> str:
    """
    Transcribe an audio file using the specified model.

    Args:
        file_path: Path to the audio file
        model: Transcription model to use

    Returns:
        Transcribed text or error message
    """
    model_info = get_model_info(model)

    if model_info.engine == "apple":
        return transcribe_file_apple_speech(file_path)

    elif model_info.engine == "whisper":
        from .whisper_transcriber import transcribe_file_whisper
        return transcribe_file_whisper(file_path, model_info.model_size or "base")

    elif model_info.engine == "faster-whisper":
        from .faster_whisper_transcriber import transcribe_file_faster_whisper
        return transcribe_file_faster_whisper(file_path, model_info.model_size or "base")

    else:
        return f"Unknown transcription engine: {model_info.engine}"

def transcribe_files(paths: list[str]) -> list[str]:
    """Transcribe multiple audio files."""
    results = []

    for p in paths:
        try:
            res_text = transcribe_file(p)
            results.append(res_text)
        except Exception as e:
            results.append(f"Failed to transcribe {p}: {str(e)}")

    return results



