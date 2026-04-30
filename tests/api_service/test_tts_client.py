from types import SimpleNamespace

from api_service.app import tts_client


def test_tts_client_builds_grpc_request(monkeypatch):
    captured = {}

    class FakeStub:
        def __init__(self, channel):
            captured["channel"] = channel

        def SynthesizeVoice(self, request):
            captured["request"] = request
            return SimpleNamespace(audio=b"grpc-audio")

    def fake_channel(address: str):
        captured["address"] = address
        return "fake-channel"

    monkeypatch.setenv("TTS_SERVICE_ADDR", "tts-service:50051")
    monkeypatch.setattr(tts_client.grpc, "insecure_channel", fake_channel)
    monkeypatch.setattr(tts_client.tts_pb2_grpc, "TTSServiceStub", FakeStub)

    audio = tts_client.synthesize_text("Hello", "amy", "en", "onnxruntime")

    assert audio == b"grpc-audio"
    assert captured["address"] == "tts-service:50051"
    assert captured["channel"] == "fake-channel"
    assert captured["request"].text == "Hello"
    assert captured["request"].voice == "amy"
    assert captured["request"].language == "en"
    assert captured["request"].environment == "onnxruntime"
    assert captured["request"].request_id
