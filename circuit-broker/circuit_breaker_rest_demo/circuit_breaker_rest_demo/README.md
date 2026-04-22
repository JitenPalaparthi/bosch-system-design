# Python Circuit Breaker REST API Demo

This demo shows a **Circuit Breaker** pattern using two REST APIs:

- **flaky-service**: a downstream service that randomly fails
- **gateway-service**: an upstream API that calls the flaky service through a circuit breaker

## Architecture

Client -> gateway-service -> Circuit Breaker -> flaky-service

When the downstream service fails repeatedly:

1. The breaker starts in **CLOSED** state
2. After repeated failures, it moves to **OPEN**
3. While **OPEN**, gateway stops calling downstream and returns fallback immediately
4. After timeout, breaker moves to **HALF_OPEN**
5. If trial calls succeed, it returns to **CLOSED**
6. If trial calls fail, it goes back to **OPEN**

## Project structure

```text
circuit_breaker_rest_demo/
├── docker-compose.yml
├── README.md
├── gateway_service/
│   ├── app.py
│   ├── breaker.py
│   ├── requirements.txt
│   └── Dockerfile
└── flaky_service/
    ├── app.py
    ├── requirements.txt
    └── Dockerfile
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Endpoints

### Gateway service
- `GET http://localhost:5000/health`
- `GET http://localhost:5000/breaker`
- `GET http://localhost:5000/proxy`

### Flaky service
- `GET http://localhost:5001/health`
- `GET http://localhost:5001/work`

## Test the breaker

Call this multiple times:

```bash
curl http://localhost:5002/proxy
```

Check breaker state:

```bash
curl http://localhost:5002/breaker
```

You will observe states such as:

- `CLOSED`
- `OPEN`
- `HALF_OPEN`

## Example responses

### Normal success
```json
{
  "breaker_state": "CLOSED",
  "downstream": {
    "message": "Work completed",
    "service": "flaky-service",
    "success": true
  },
  "success": true
}
```

### Open breaker fallback
```json
{
  "breaker_state": "OPEN",
  "message": "Fallback response because circuit is open",
  "success": false
}
```

## Tune behavior

Change these variables in `docker-compose.yml`:

- `FAILURE_RATE`: probability that flaky service fails (0.0 to 1.0)
- `FAILURE_THRESHOLD`: failures before opening breaker
- `RECOVERY_TIMEOUT`: seconds before trying half-open
- `SUCCESS_THRESHOLD`: successful half-open requests needed to close breaker
- `REQUEST_TIMEOUT`: timeout for downstream HTTP request

## Run locally without Docker

### Flaky service
```bash
cd flaky_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Gateway service
Open another terminal:

```bash
cd gateway_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DOWNSTREAM_URL=http://localhost:5001/work
python app.py
```

## Learning points

- Fail fast when a dependency is unhealthy
- Protect upstream service from cascading failures
- Use fallback responses when downstream is unstable
- Recover automatically after cooldown period
