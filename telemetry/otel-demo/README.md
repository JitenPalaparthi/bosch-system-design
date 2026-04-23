# OpenTelemetry Full Demo 

This package is a corrected version of the original demo.

## Run

```bash
docker compose down -v
docker compose pull
docker compose up --build -d
```

## Open

- App: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Loki readiness: http://localhost:3100/ready
- Tempo status: http://localhost:3200/status/usage-stats

Grafana login: `admin / admin`

## Generate telemetry

```bash
curl http://localhost:8000/
curl "http://localhost:8000/work?delay_ms=150&fanout_calls=2"
curl -X POST "http://localhost:8000/orders/laptop?quantity=2"
curl http://localhost:8000/orders
curl http://localhost:8000/error
curl "http://localhost:8000/burst?n=25"
```

## Grafana

In Explore:
- Prometheus datasource: query `demo_requests_total`
- Loki datasource: query `{service_name="orders-api"}`
- Tempo datasource: search recent traces for service `orders-api`

## Troubleshooting

```bash
docker compose ps
docker logs grafana
docker logs loki
docker logs tempo
docker logs otel-collector
docker logs otel-demo-app
```

If Grafana says a datasource is not connected, verify the datasource URL uses the Docker service names:
- `http://prometheus:9090`
- `http://loki:3100`
- `http://tempo:3200`


## Fast verification

After startup, generate telemetry and inspect the Collector debug stream:

```bash
curl http://localhost:8000/
curl "http://localhost:8000/work?delay_ms=150&fanout_calls=2"
docker logs otel-collector --tail 100
```

If the Collector log shows `ResourceSpans` and `LogRecord`, the app → Collector path is working even before Grafana queries are checked.
