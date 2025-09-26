import Speech
import time
import Foundation

def transcribe_file(file_path: str) -> str:
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



