# gRPC TTS Service

Учебный проект микросервисного backend-сервиса для синтеза речи.

Проект состоит из двух сервисов:

- `api_service` — HTTP API на FastAPI. Принимает пользовательский запрос, валидирует текст и отправляет его в TTS-сервис по gRPC.
- `tts-service` — gRPC-сервис на Python. Получает текст, запускает Piper TTS и возвращает WAV-аудио.

Общение между сервисами описано в protobuf-контракте `proto/tts.proto`.

## Архитектура

```text
client
  -> POST /synthesize
  -> api_service, FastAPI
  -> gRPC
  -> tts-service
  -> Piper model
  -> WAV response
```

## Структура

```text
.
├── api_service/          # FastAPI gateway
│   ├── app/
│   │   ├── main.py       # HTTP endpoints
│   │   ├── schemas.py    # request schemas
│   │   ├── validation.py # input validation
│   │   └── tts_client.py # gRPC client for tts-service
│   ├── Dockerfile
│   └── requirements.txt
│
├── tts-service/          # gRPC TTS service
│   ├── app/
│   │   ├── server.py      # gRPC server
│   │   └── synthesizer.py # Piper wrapper
│   ├── Dockerfile
│   └── requirements.txt
│
├── proto/
│   └── tts.proto          # protobuf/gRPC contract
│
├── generated/             # generated Python protobuf files
├── models/piper/          # local Piper model files, ignored by git
├── qt_client/              # desktop frontend на C++/Qt
├── k8s/                   # Kubernetes manifests
└── run_k8s.sh             # helper script for local kind deployment
```

## Локальный запуск

Создать и активировать виртуальное окружение:

```bash
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
```

Установить зависимости:

```bash
python -m pip install -r api_service/requirements.txt
python -m pip install -r tts-service/requirements.txt
```

Скачать Piper-модель:

```bash
mkdir -p models/piper

curl -L \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx?download=true" \
  -o models/piper/en_US-amy-low.onnx

curl -L \
  "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/low/en_US-amy-low.onnx.json?download=true" \
  -o models/piper/en_US-amy-low.onnx.json
```

Запустить gRPC TTS-сервис:

```bash
source .venv/bin/activate
PIPER_MODEL_PATH=models/piper/en_US-amy-low.onnx \
python tts-service/app/server.py
```

В другом терминале запустить FastAPI:

```bash
source .venv/bin/activate
uvicorn api_service.app.main:app --reload
```

Проверить API:

```bash
curl http://127.0.0.1:8000/health
```

Отправить запрос на синтез:

```bash
curl -X POST http://127.0.0.1:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from FastAPI and gRPC","voice":"default"}' \
  --output result.wav
```

## Desktop frontend на C++/Qt

В проект добавлен минимальный Qt-клиент `qt_client`.

Он умеет:

- вводить текст запроса и voice;
- отправлять `POST /synthesize` в `api_service`;
- получать WAV-ответ и прослушивать его через `QMediaPlayer`;
- сохранять WAV в выбранный файл;
- автоматически удалять временный WAV, если пользователь его не сохранил.

Требования:

- Qt 6 с модулями `Widgets`, `Network`, `Multimedia`;
- CMake 3.21+;
- запущенные `tts-service` и `api_service`.

Сборка:

```bash
cmake -S qt_client -B qt_client/build
cmake --build qt_client/build
```

Если CMake не находит Qt на macOS, установите Qt и передайте путь к нему:

```bash
brew install qt
cmake -S qt_client -B qt_client/build \
  -DCMAKE_PREFIX_PATH="$(brew --prefix qt)"
cmake --build qt_client/build
```

Запуск:

```bash
./qt_client/build/tts_qt_client
```

По умолчанию клиент отправляет запросы на:

```text
http://127.0.0.1:8000/synthesize
```

## Генерация protobuf-классов

Если изменился `proto/tts.proto`, нужно пересгенерировать Python-код:

```bash
source .venv/bin/activate
python -m grpc_tools.protoc \
  -I proto \
  --python_out=generated \
  --grpc_python_out=generated \
  proto/tts.proto
```

## Kubernetes

Проект можно запустить локально в `kind`.

Создать кластер:

```bash
kind create cluster --name tts-dev --image kindest/node:v1.32.2
```

Далее можно либо запустить скрипт
```bash
./run_k8s.sh
```

Либо прописать команды ниже. Собрать Docker-образы:

```bash
docker build -t api-service:local -f api_service/Dockerfile .
docker build -t tts-service:local -f tts-service/Dockerfile .
```

Загрузить образы в `kind`:

```bash
kind load docker-image api-service:local --name tts-dev
kind load docker-image tts-service:local --name tts-dev
```

Применить Kubernetes-манифесты:

```bash
kubectl apply -f k8s/
```

Проверить состояние:

```bash
kubectl get pods
kubectl get services
```

Пробросить API на локальную машину:

```bash
kubectl port-forward service/api-service 8000:8000
```

Отправить запрос:

```bash
curl -X POST http://127.0.0.1:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from Kubernetes","voice":"default"}' \
  --output result.wav
```
