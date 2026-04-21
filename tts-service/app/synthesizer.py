import subprocess
import tempfile
from pathlib import Path


class PiperSynthesizer:
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
