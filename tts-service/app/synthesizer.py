import subprocess
import tempfile
from pathlib import Path
import io
import wave
from piper.voice import PiperVoice


class PiperCliSynthesizer:
    def __init__(self, model_path: str):
        self.model_path = model_path

    def synthesize(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav") as output_file:
            subprocess.run(
                [
                    "piper",
                    "--model",
                    self.model_path,
                    "--output_file",
                    output_file.name,
                ],
                input=text,
                text=True,
                check=True,
            )

            return Path(output_file.name).read_bytes()

class PiperORTSynthesizer:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.voice = PiperVoice.load(model_path)

    def synthesize(self, text: str) -> bytes:
        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)

        return wav_buffer.getvalue()