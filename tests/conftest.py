import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT_DIR / "generated"
TTS_APP_DIR = ROOT_DIR / "tts-service" / "app"

for path in (ROOT_DIR, GENERATED_DIR, TTS_APP_DIR):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
