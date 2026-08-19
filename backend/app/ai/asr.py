import io
import wave
from faster_whisper import WhisperModel

# Initialize lightweight local Whisper model
model_size = "base"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

def transcribe_audio_bytes(audio_bytes: bytes, language: str = "en") -> str:
    """Transcribes raw WAV/PCM audio bytes into text."""
    try:
        audio_stream = io.BytesIO(audio_bytes)
        segments, _ = model.transcribe(audio_stream, language=language, beam_size=1)
        transcript = " ".join([segment.text for segment in segments]).strip()
        return transcript
    except Exception as e:
        print(f"[ASR Error]: {e}")
        return ""

if __name__ == "__main__":
    print("Whisper ASR model loaded successfully.")