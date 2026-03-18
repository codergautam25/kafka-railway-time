
# Enterprise Event-Driven Streaming Platform

## Stack
- FastAPI (API Layer)
- Kafka + Schema Registry
- ksqlDB (stream processing)
- Redis (cache)
- Prometheus + Grafana (observability)
- OpenTelemetry (tracing)
- JWT + API Gateway (security)
- Docker Compose (deployment)

## Architecture Flow
Client → API Gateway → FastAPI → Kafka → ksqlDB → Kafka → Consumer → Redis → API

## Run
docker-compose up --build

## Observability
- Prometheus: localhost:9090
- Grafana: localhost:3000

## Security
- JWT Auth
- API Gateway layer

## Topics
- user-events
- enriched-events
- fraud-alerts
