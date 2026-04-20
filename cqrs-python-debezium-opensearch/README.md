# CQRS Demo with Python, PostgreSQL, Kafka, Debezium, and OpenSearch

This project demonstrates a practical **CQRS** setup using:

- **Command side**: Python Flask service writing to PostgreSQL
- **CDC pipeline**: PostgreSQL -> Debezium -> Kafka
- **Projection**: Python projector service consuming Debezium CDC events from Kafka
- **Read side**: OpenSearch index queried by a separate Python Flask query service
- **Observability / UI**:
  - Kafka UI
  - Kafka Connect REST
  - OpenSearch Dashboards

## Architecture

```text
                 +------------------------+
                 |        Client          |
                 +-----------+------------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
   +---------------------+       +----------------------+
   | Command Service     |       | Query Service        |
   | POST /orders        |       | GET /query/orders    |
   +----------+----------+       +----------+-----------+
              |                             |
              v                             v
   +---------------------+       +----------------------+
   | PostgreSQL          |       | OpenSearch           |
   | Write model         |       | Read model           |
   +----------+----------+       +----------------------+
              |
              | WAL / logical decoding
              v
   +---------------------+
   | Debezium Connector  |
   | Kafka Connect       |
   +----------+----------+
              |
              v
   +---------------------+
   | Kafka topic         |
   | cdc.public.orders   |
   +----------+----------+
              |
              v
   +---------------------+
   | Projector Service   |
   | transforms CDC      |
   +---------------------+
```

## Ports

No service uses port **5000**.

- Command Service: `8001`
- Query Service: `8003`
- Kafka Connect REST: `8083`
- Kafka UI: `8090`
- PostgreSQL: `5432`
- OpenSearch: `9200`
- OpenSearch Dashboards: `5601`
- Kafka broker: `9092`

## Project Layout

```text
cqrs-python-debezium-opensearch/
├── command-service/
├── query-service/
├── projector-service/
├── postgres-init/
├── connectors/
├── scripts/
├── docker-compose.yml
└── README.md
```

## How It Works

1. The **command service** inserts or updates rows in PostgreSQL.
2. PostgreSQL logical decoding exposes row changes in WAL.
3. The **Debezium PostgreSQL connector** captures those changes and emits CDC events to Kafka.
4. The **projector service** consumes the Kafka CDC topic and builds a query-optimized OpenSearch document.
5. The **query service** serves search/filter APIs from OpenSearch.

## Start the Stack

```bash
docker compose up --build
```

The first startup can take a bit because Docker pulls several images.

## Verify Services

### 1) Kafka Connect

```bash
curl http://localhost:8083/connectors
```

Expected connector name:

```json
["postgres-orders-source"]
```

### 2) Connector status

```bash
curl http://localhost:8083/connectors/postgres-orders-source/status
```

### 3) Kafka UI

Open:

```text
http://localhost:8090
```

You should see:
- cluster `local`
- Kafka Connect instance `debezium-connect`
- topic `cdc.public.orders`

### 4) OpenSearch

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### 5) Dashboards

Open:

```text
http://localhost:5601
```

## Command Side Examples

### Create an order

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-101",
    "customer_name": "Jiten",
    "item": "Laptop",
    "quantity": 1,
    "price": 85000
  }'
```

### Create another order

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-102",
    "customer_name": "Asha",
    "item": "Keyboard",
    "quantity": 2,
    "price": 2500
  }'
```

### Cancel an order

```bash
curl -X POST http://localhost:8001/orders/<ORDER_ID>/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason":"customer_request"}'
```

### Ship an order

```bash
curl -X POST http://localhost:8001/orders/<ORDER_ID>/ship \
  -H "Content-Type: application/json" \
  -d '{"tracking_id":"TRK-90001"}'
```

### Inspect write-side rows directly through API

```bash
curl http://localhost:8001/orders-write
```

## Query Side Examples

### List all indexed orders

```bash
curl http://localhost:8003/query/orders
```

### Filter by status

```bash
curl "http://localhost:8003/query/orders?status=CREATED"
```

### Filter by customer_id

```bash
curl "http://localhost:8003/query/orders?customer_id=CUST-101"
```

### Full-text search

```bash
curl "http://localhost:8003/query/orders/search?q=laptop"
```

### Dashboard aggregation

```bash
curl http://localhost:8003/query/dashboard/status-counts
```

## Kafka Topic Produced by Debezium

Connector topic:

```text
cdc.public.orders
```

A typical CDC message from Debezium includes:

- `before`
- `after`
- `op`
- `source`
- timestamps

The projector looks at `op`:

- `c` = create
- `r` = snapshot read
- `u` = update
- `d` = delete

and updates the OpenSearch read model accordingly.

## Important Files

### `connectors/postgres-orders-source.json`
Debezium PostgreSQL source connector configuration.

### `scripts/register-connector.sh`
Waits for Kafka Connect and registers the connector automatically.

### `projector-service/app.py`
Consumes CDC events and builds the OpenSearch read model.

## Troubleshooting

### Kafka Connect shows no connector

Run:

```bash
curl http://localhost:8083/connectors
```

If empty, inspect init container logs:

```bash
docker logs cqrs-connector-init
```

### Connector failed

```bash
curl http://localhost:8083/connectors/postgres-orders-source/status | jq
```

If `jq` is not installed:

```bash
curl http://localhost:8083/connectors/postgres-orders-source/status
```

### Command side writes but query side is empty

Check projector logs:

```bash
docker logs cqrs-projector-service
```

Check Kafka topic exists in Kafka UI.

### OpenSearch not reachable

```bash
curl http://localhost:9200
```

If OpenSearch fails on low-memory machines, increase Docker memory allocation.

### Rebuild from scratch

```bash
docker compose down -v
docker compose up --build
```

## Notes

- This project intentionally uses **Debezium CDC** rather than direct Kafka publishing from the command service.
- That keeps the **write path** focused on transactions in PostgreSQL, while the event pipeline is derived from database changes.
- For a production system, you would usually add:
  - authentication / authorization
  - schema governance
  - connector secrets management
  - dead-letter handling
  - replay / reindex strategy
  - idempotency strategy in the projector
  - stronger monitoring and alerting

## Optional Manual Connector Registration

If you ever want to register the connector manually instead of relying on the init container:

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @connectors/postgres-orders-source.json
```

## Summary

This demo shows a realistic CQRS split:

- **Command model** -> PostgreSQL
- **Change capture** -> Debezium on Kafka Connect
- **Event transport** -> Kafka
- **Read model projection** -> OpenSearch
- **Query model** -> dedicated Python query API

