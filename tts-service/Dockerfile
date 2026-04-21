FROM python:3.12-slim

WORKDIR /app

COPY tts-service/requirements.txt /app/tts-service/requirements.txt
RUN pip install --no-cache-dir -r /app/tts-service/requirements.txt

COPY tts-service /app/tts-service
COPY models /app/models
COPY generated /app/generated

ENV PYTHONPATH=/app/generated
ENV PIPER_MODEL_PATH=/app/models/piper/en_US-amy-low.onnx

EXPOSE 50051

CMD ["python", "/app/tts-service/app/server.py"]
