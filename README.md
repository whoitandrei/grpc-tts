# TTS Service

Learning project for a small microservice-based text-to-speech backend.

The current architecture is:

```text
client
  -> HTTP POST /synthesize
  -> api_service, FastAPI
  -> gRPC call
  -> tts-service, Python gRPC server
  -> Piper TTS model
  -> WAV bytes back to the client
```

## Project Layout

```text
api_service/       FastAPI HTTP gateway
tts-service/       gRPC text-to-speech service
proto/             protobuf contract
generated/         generated Python protobuf/gRPC classes
k8s/               Kubernetes manifests
models/piper/      local Piper model files, not committed to git
run_k8s.sh         local helper script for kind
```

## Local Setup

Create and activate a Python virtual environment:

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r api_service/requirements.txt
python -m pip install -r tts-service/requirements.txt
```

## Download Piper Model

Model files are intentionally ignored by git. Download them before running the real TTS service:

```bash
mkdir -p models/piper

curl -L \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx?download=true" \
  -o models/piper/en_US-amy-low.onnx

curl -L \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx.json?download=true" \
  -o models/piper/en_US-amy-low.onnx.json
```

Quick model check:

```bash
echo "Hello from Piper" | piper \
  --model models/piper/en_US-amy-low.onnx \
  --output_file test.wav
```

## Run Locally

Terminal 1, start the gRPC TTS service:

```bash
source .venv/bin/activate
PIPER_MODEL_PATH=models/piper/en_US-amy-low.onnx \
python tts-service/app/server.py
```

Terminal 2, start the FastAPI gateway:

```bash
source .venv/bin/activate
uvicorn api_service.app.main:app --reload
```

Terminal 3, send a request:

```bash
curl -X POST http://127.0.0.1:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from FastAPI and gRPC","voice":"default"}' \
  --output result.wav
```

## Regenerate gRPC Code

If `proto/tts.proto` changes, regenerate Python classes:

```bash
source .venv/bin/activate
python -m grpc_tools.protoc \
  -I proto \
  --python_out=generated \
  --grpc_python_out=generated \
  proto/tts.proto
```

## Run in Kubernetes with kind

Create a local cluster:

```bash
kind create cluster --name tts-dev --image kindest/node:v1.32.2
```

Build and load local images:

```bash
docker build -t api-service:local -f api_service/Dockerfile .
docker build -t tts-service:local -f tts-service/Dockerfile .

kind load docker-image api-service:local --name tts-dev
kind load docker-image tts-service:local --name tts-dev
```

Apply manifests:

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

Forward the API service to localhost:

```bash
kubectl port-forward service/api-service 8000:8000
```

Send a request:

```bash
curl -X POST http://127.0.0.1:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Kubernetes","voice":"default"}' \
  --output result.wav
```

## GitHub

Initialize, commit, and push:

```bash
git add .
git commit -m "Initial TTS microservices scaffold"
git branch -M main
git remote add origin git@github.com:<your-user>/<your-repo>.git
git push -u origin main
```

