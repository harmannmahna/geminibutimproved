import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os


class VoiceHandler:
    def __init__(self, model_size: str = "base"):
        """
        model_size options and their trade-offs:
          tiny   → ~39MB,  fastest, least accurate
          base   → ~74MB,  good balance  ← recommended for dev
          small  → ~244MB, more accurate, slower
          medium → ~769MB, very accurate, needs good GPU

        First run downloads the model and caches it in ~/.cache/whisper/
        After that it loads instantly.
        """
        print(f"Loading Whisper '{model_size}' model... (first run ~30s)")
        self.whisper_model = whisper.load_model(model_size)
        self.sample_rate = 16000  # Whisper expects 16kHz

    def record_audio(self, duration_seconds: int = 10) -> np.ndarray:
        """
        Records from the default system microphone.
        Returns a numpy float32 array of raw audio samples.
        """
        print(f"🎙  Recording for {duration_seconds}s... speak now!")
        audio = sd.rec(
            int(duration_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()  # blocks until recording finishes
        print("✅ Recording done.")
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe a numpy audio array to text.
        Whisper needs a WAV file on disk, so we use a temp file.
        """
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            wav.write(tmp_path, self.sample_rate, audio)

        try:
            result = self.whisper_model.transcribe(tmp_path, language="en")
            return result["text"].strip()
        finally:
            os.unlink(tmp_path)  # always clean up

    def record_and_transcribe(self, duration_seconds: int = 10) -> str:
        """Convenience wrapper: record → transcribe → return text."""
        audio = self.record_audio(duration_seconds)
        return self.transcribe(audio)