# Python Circuit Breaker Demo

This is a simple **Circuit Breaker pattern** demo in Python.

## What it shows

- **CLOSED** state: requests are allowed
- **OPEN** state: requests are blocked after repeated failures
- **HALF_OPEN** state: a trial request is allowed after timeout
- **Fallback** response when the main service fails

## Files

- `breaker.py` - circuit breaker implementation
- `unstable_service.py` - fake unstable remote API
- `demo.py` - runnable demo script
- `requirements.txt` - dependencies file

## Run

```bash
python3 demo.py
```

## How it works

1. The app calls a simulated unstable API.
2. If failures keep happening, the breaker opens.
3. While open, calls are blocked immediately.
4. After timeout, it moves to half-open.
5. If the trial call succeeds, it closes again.
6. If the trial call fails, it reopens.

## Expected learning outcome

You can use this exact pattern in:

- microservices
- payment gateways
- third-party API calls
- database access protection
- message broker dependent services

## Next extension ideas

- Wrap HTTP calls using `requests`
- Add Flask/FastAPI endpoints
- Add metrics and logging
- Integrate with Redis/Kafka demo
