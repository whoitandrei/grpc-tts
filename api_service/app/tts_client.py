import os
import sys
import uuid
from pathlib import Path

import grpc

ROOT_DIR = Path(__file__).resolve().parents[2]
GENERATED_DIR = ROOT_DIR / "generated"
sys.path.insert(0, str(GENERATED_DIR))

import tts_pb2
import tts_pb2_grpc


def synthesize_text(text: str, voice: str, language: str) -> bytes:
    tts_service_addr = os.getenv("TTS_SERVICE_ADDR", "localhost:50051")
    channel = grpc.insecure_channel(tts_service_addr)

    stub = tts_pb2_grpc.TTSServiceStub(channel)

    request = tts_pb2.SynthesizeRequest(
        text=text,
        voice=voice,
        language=language,
        request_id=str(uuid.uuid4()),
    )

    response = stub.SynthesizeVoice(request)

    return response.audio
