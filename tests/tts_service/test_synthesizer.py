import subprocess
from pathlib import Path

import synthesizer as synthesizer_module


def test_synthesizer_runs_piper_and_reads_wav(monkeypatch):
    captured = {}

    def fake_run(command, input=None, text=None, check=None):
        captured["command"] = command
        captured["input"] = input
        captured["text"] = text
        captured["check"] = check

        output_index = command.index("--output_file") + 1
        output_path = Path(command[output_index])
        output_path.write_bytes(b"RIFFunit-test-audio")

        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(synthesizer_module.subprocess, "run", fake_run)

    synthesizer = synthesizer_module.PiperSynthesizer("models/piper/en_US-amy-low.onnx")
    audio = synthesizer.synthesize("Hello from Piper")

    assert audio == b"RIFFunit-test-audio"
    assert captured["command"] == [
        "piper",
        "--model",
        "models/piper/en_US-amy-low.onnx",
        "--output_file",
        captured["command"][4],
    ]
    assert captured["input"] == "Hello from Piper"
    assert captured["text"] is True
    assert captured["check"] is True
