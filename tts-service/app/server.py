from concurrent import futures
import sys
from pathlib import Path
import os
from synthesizer import PiperSynthesizer

import grpc

ROOT_DIR = Path(__file__).resolve().parents[2]
GENERATED_DIR = ROOT_DIR / "generated"
sys.path.insert(0, str(GENERATED_DIR))

import tts_pb2
import tts_pb2_grpc

class TTSService(tts_pb2_grpc.TTSServiceServicer):
    def SynthesizeVoice(self, request, context):
        print(f"text={request.text}")
        print(f"voice={request.voice}")
        print(f"request_id={request.request_id}")

        MODEL_PATH = os.getenv("PIPER_MODEL_PATH", "models/piper/en_US-amy-low.onnx")
        synthesizer = PiperSynthesizer(MODEL_PATH)

        audio_data = synthesizer.synthesize(request.text)

        return tts_pb2.SynthesizeResponse(
            audio=audio_data,
            filename=f"{request.request_id}.wav",
            content_type="audio/wav",
            request_id=request.request_id,
        )

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tts_pb2_grpc.add_TTSServiceServicer_to_server(TTSService(), server,)
    server.add_insecure_port("[::]:50051")
    server.start()

    print("TTS Service is running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    main()