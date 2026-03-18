
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn confluent-kafka redis pyjwt
