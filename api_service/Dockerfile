FROM python:3.12-slim

WORKDIR /app

COPY api_service/requirements.txt /app/api_service/requirements.txt
RUN pip install --no-cache-dir -r /app/api_service/requirements.txt

COPY api_service /app/api_service
COPY generated /app/generated

ENV PYTHONPATH=/app:/app/generated

EXPOSE 8000

CMD ["uvicorn", "api_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
