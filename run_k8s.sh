#!/bin/bash

docker build -t api-service:local -f api_service/Dockerfile .
docker build -t tts-service:local -f tts-service/Dockerfile .

kind load docker-image api-service:local --name tts-dev
kind load docker-image tts-service:local --name tts-dev

kubectl apply -f k8s/

kubectl get pods
kubectl get services

kubectl port-forward service/api-service 8000:8000