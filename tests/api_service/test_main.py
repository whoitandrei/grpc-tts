from fastapi.testclient import TestClient

from api_service.app import main as main_module


client = TestClient(main_module.app)


def test_synthesize_returns_wav_audio(monkeypatch):
    captured = {}

    def fake_synthesize(text: str, voice: str, language: str, environment: str) -> bytes:
        captured["args"] = (text, voice, language, environment)
        return b"RIFFdemo-audio"

    monkeypatch.setattr(main_module, "synthesize_text", fake_synthesize)

    response = client.post(
        "/synthesize",
        json={
            "text": "Hello from test",
            "voice": "default",
            "language": "en",
            "environment": "onnxruntime",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"RIFFdemo-audio"
    assert captured["args"] == ("Hello from test", "default", "en", "onnxruntime")


def test_synthesize_uses_request_defaults(monkeypatch):
    captured = {}

    def fake_synthesize(text: str, voice: str, language: str, environment: str) -> bytes:
        captured["args"] = (text, voice, language, environment)
        return b"RIFFdefault-audio"

    monkeypatch.setattr(main_module, "synthesize_text", fake_synthesize)

    response = client.post(
        "/synthesize",
        json={"text": "Only text provided"},
    )

    assert response.status_code == 200
    assert captured["args"] == ("Only text provided", "default", "en", "onnxruntime")


def test_synthesize_rejects_unsupported_language(monkeypatch):
    called = {"value": False}

    def fake_synthesize(*args, **kwargs) -> bytes:
        called["value"] = True
        return b""

    monkeypatch.setattr(main_module, "synthesize_text", fake_synthesize)

    response = client.post(
        "/synthesize",
        json={
            "text": "Privet",
            "voice": "default",
            "language": "ru",
            "environment": "onnxruntime",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only EN are supported now"}
    assert called["value"] is False
