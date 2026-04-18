# CQRS Demo: FastAPI + PostgreSQL + Debezium + Kafka + OpenSearch

This project is a **simple, end-to-end CQRS / CDC demo**.

## What it demonstrates

- **Write side**: a Python FastAPI REST API writes data to **PostgreSQL**
- **CDC**: **Debezium** captures row changes from PostgreSQL and publishes them to **Kafka**
- **Projection**: a Python consumer reads those Kafka CDC events and writes a read model into **OpenSearch**
- **Read side**: a separate Python FastAPI REST API reads from **OpenSearch**

## Architecture

```text
                WRITE SIDE                                  READ SIDE
+---------------------------+                      +------------------------+
| FastAPI Write API         |                      | FastAPI Read API       |
| http://localhost:8000     |                      | http://localhost:8001  |
+------------+--------------+                      +-----------+------------+
             |                                                 |
             | INSERT / UPDATE / DELETE                        | SEARCH / GET
             v                                                 v
+---------------------------+                      +------------------------+
| PostgreSQL                |                      | OpenSearch             |
| localhost:5432            |                      | localhost:9200         |
+------------+--------------+                      +------------------------+
             |
             | WAL / logical decoding (pgoutput)
             v
+---------------------------+
| Debezium on Kafka Connect |
| localhost:8083            |
+------------+--------------+
             |
             | CDC events
             v
+---------------------------+
| Kafka                     |
| localhost:9092            |
+------------+--------------+
             |
             | consume + project
             v
+---------------------------+
| Python projector          |
| upserts/deletes documents |
+---------------------------+
```

## Containers included

- `postgres`
- `zookeeper`
- `kafka`
- `kafka-connect` (Debezium Connect)
- `connector-init` (registers Debezium PostgreSQL connector automatically)
- `opensearch`
- `opensearch-dashboards`
- `write-api`
- `read-api`
- `projector`

## Ports

- Write API: `8000`
- Read API: `8001`
- PostgreSQL: `5432`
- Kafka Connect: `8083`
- Kafka: `9092`
- OpenSearch: `9200`
- OpenSearch Dashboards: `5601`

---

## Prerequisites

Install:

- Docker
- Docker Compose

Recommended Docker memory: **at least 6 GB**.

---

## Start the stack

From the project directory:

```bash
docker compose up --build
```

Run in detached mode if you prefer:

```bash
docker compose up --build -d
```

---

## Verify services

### 1) Check write API

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok","service":"write-api"}
```

### 2) Check read API

```bash
curl http://localhost:8001/health
```

Expected:

```json
{"status":"ok","service":"read-api"}
```

### 3) Check Kafka Connect connector list

```bash
curl http://localhost:8083/connectors
```

Expected output should include:

```json
["postgres-products-connector"]
```

### 4) Check OpenSearch

```bash
curl http://localhost:9200
```

---

## End-to-end demo steps

## Create a product through the write API

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "16GB RAM developer laptop",
    "price": 65000,
    "category": "electronics"
  }'
```

Expected response:

```json
{
  "message": "written to postgres",
  "product": {
    "id": 1,
    "name": "Laptop",
    "description": "16GB RAM developer laptop",
    "price": 65000.0,
    "category": "electronics",
    "created_at": "...",
    "updated_at": "..."
  }
}
```

At this point the flow is:

1. Write API inserts into PostgreSQL
2. Debezium reads the committed row change from PostgreSQL WAL
3. Debezium publishes a CDC event to Kafka topic `dbserver1.public.products`
4. The projector consumes that event
5. The projector upserts a document into OpenSearch index `products`

Because this is asynchronous, wait a second or two if needed before querying the read side.

---

## Read all products from OpenSearch via read API

```bash
curl http://localhost:8001/products
```

Expected output should include the inserted product.

---

## Search products from OpenSearch

```bash
curl "http://localhost:8001/products/search?q=laptop"
```

---

## Get a single product by ID from OpenSearch

```bash
curl http://localhost:8001/products/1
```

---

## Update a product through the write API

```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 70000,
    "description": "Updated description after CDC"
  }'
```

Then query the read model again:

```bash
curl http://localhost:8001/products/1
```

You should see the updated value after the CDC pipeline propagates it.

---

## Delete a product through the write API

```bash
curl -X DELETE http://localhost:8000/products/1
```

Then list products:

```bash
curl http://localhost:8001/products
```

The document should disappear from OpenSearch.

---

## Inspect what Debezium is publishing

You can inspect Kafka Connect status:

```bash
curl http://localhost:8083/connectors/postgres-products-connector/status
```

And inspect projector logs:

```bash
docker compose logs -f projector
```

Look for messages such as:

- `Received event op=c`
- `Received event op=u`
- `Received event op=d`
- `Indexed document id=...`
- `Deleted document id=...`

---

## Important concepts explained

## Why PostgreSQL is the source of truth

The write API only writes to PostgreSQL. This is the **authoritative transactional store**.

## Why OpenSearch is only the read model

OpenSearch is optimized for read-heavy use cases:

- search
- filtering
- denormalized views
- analytics-oriented querying

It is **not** the transactional system of record in this project.

## Why Debezium is used

Debezium provides **CDC (Change Data Capture)**. It watches committed row-level changes in PostgreSQL and turns them into Kafka events.

## Why Kafka is used

Kafka decouples the database from downstream consumers. It allows:

- durable event transport
- replayability
- multiple consumers
- loose coupling

## Why eventual consistency happens

A write reaches PostgreSQL first. The read side becomes visible **after** Debezium emits the event and the projector updates OpenSearch.

So this architecture is **eventually consistent**, not instantly consistent.

---

## Useful URLs

- Write API docs: `http://localhost:8000/docs`
- Read API docs: `http://localhost:8001/docs`
- OpenSearch Dashboards: `http://localhost:5601`
- Kafka Connect REST: `http://localhost:8083`

---

## Project structure

```text
cqrs-debezium-opensearch-demo/
├── docker-compose.yml
├── README.md
├── connector-init/
│   ├── postgres-connector.json
│   └── register-connector.sh
├── postgres-init/
│   └── init.sql
├── write-api/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── read-api/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── consumer/
    ├── Dockerfile
    ├── projector.py
    └── requirements.txt
```

---

## Tear down

```bash
docker compose down -v
```

This removes containers, networks, and volumes.

---

## Notes

- OpenSearch 3 is used in single-node mode for simplicity.
- Security is disabled for local demo simplicity.
- This project favors readability and training value over production hardening.
- In production, you would usually add:
  - retry / DLQ patterns
  - schema management
  - authentication / TLS
  - observability
  - idempotent projection logic with stronger guarantees
  - proper topic partitioning and scaling

---

## Common troubleshooting

### 1) OpenSearch is slow to start
Wait a bit longer and check:

```bash
docker compose logs -f opensearch
```

### 2) Connector is not registered
Check:

```bash
docker compose logs -f connector-init
```

### 3) Projector does not receive events
Check:

```bash
docker compose logs -f projector
```

Also verify connector status:

```bash
curl http://localhost:8083/connectors/postgres-products-connector/status
```

### 4) Read API shows nothing immediately after write
That is expected for a brief moment. This system is eventually consistent.

---

## Suggested training flow

Use this sequence while demonstrating:

1. Open Write API docs
2. Create a product
3. Show PostgreSQL contains the row
4. Show Debezium connector status
5. Show projector logs consuming `c` / `u` / `d` events
6. Query OpenSearch from the Read API
7. Update the product and show propagation
8. Delete the product and show removal from read model

