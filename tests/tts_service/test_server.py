import server as server_module
import tts_pb2


def test_grpc_server_returns_audio_response(monkeypatch):
    captured = {}

    class FakeSynthesizer:
        def __init__(self, model_path: str):
            captured["model_path"] = model_path

        def synthesize(self, text: str) -> bytes:
            captured["text"] = text
            return b"wave-bytes"

    monkeypatch.setenv("PIPER_MODEL_PATH", "models/piper/test-model.onnx")
    monkeypatch.setattr(server_module, "PiperCliSynthesizer", FakeSynthesizer)

    request = tts_pb2.SynthesizeRequest(
        text="Hello from gRPC",
        voice="default",
        language="en",
        request_id="req-123",
    )

    response = server_module.TTSService().SynthesizeVoice(request, context=None)

    assert captured["model_path"] == "models/piper/test-model.onnx"
    assert captured["text"] == "Hello from gRPC"
    assert response.audio == b"wave-bytes"
    assert response.filename == "req-123.wav"
    assert response.content_type == "audio/wav"
    assert response.request_id == "req-123"
