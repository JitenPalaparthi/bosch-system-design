# Python Saga Pattern Demo with Kafka and Docker Compose

This project demonstrates an **orchestration-based Saga pattern** using:

- **Order Service** (Python + Flask): starts the saga and acts as the orchestrator
- **Payment Service** (Python + Flask): saga participant
- **Kafka**: event backbone
- **Kafka UI**: inspect topics and messages
- **SQLite**: local persistence inside each service container
- **Docker Compose**: runs the entire demo

No service uses port **5000**.

## Architecture

```text
Client
  |
  v
Order Service (8001)  ---> writes local order as PENDING
  |
  | publishes ORDER_CREATED and PAYMENT_REQUESTED
  v
Kafka
  |
  v
Payment Service (8002)
  |
  | local payment transaction
  |-- success --> PAYMENT_COMPLETED
  |-- failure --> PAYMENT_FAILED
  v
Kafka
  |
  v
Order Service Consumer
  |-- PAYMENT_COMPLETED -> CONFIRMED
  |-- PAYMENT_FAILED    -> CANCELLED (compensation)
```

## Saga Pattern Used Here

This demo uses **orchestration**:

1. Client calls **Order Service**.
2. Order Service creates a local order record with status `PENDING`.
3. Order Service publishes `PAYMENT_REQUESTED`.
4. Payment Service consumes the event and performs its local transaction.
5. On success, Payment Service publishes `PAYMENT_COMPLETED`.
6. On failure, Payment Service publishes `PAYMENT_FAILED`.
7. Order Service consumes the result:
   - success -> updates order to `CONFIRMED`
   - failure -> updates order to `CANCELLED` and publishes `ORDER_CANCELLED`

## Services and Ports

- Order Service: `http://localhost:8001`
- Payment Service: `http://localhost:8002`
- Kafka broker exposed on: `localhost:9092`
- Kafka UI: `http://localhost:8090`

## Folder Structure

```text
saga-kafka-demo/
├── docker-compose.yml
├── README.md
├── order-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── payment-service/
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

## Start the Demo

```bash
docker compose up --build
```

To run in detached mode:

```bash
docker compose up --build -d
```

## Health Checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Test 1: Successful Saga

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-101",
    "item": "laptop-bag",
    "amount": 299,
    "card_number": "4111111111111111"
  }'
```

Then verify:

```bash
curl http://localhost:8001/orders
curl http://localhost:8002/payments
```

Expected result:

- order becomes `CONFIRMED`
- payment becomes `APPROVED`

## Test 2: Failed Saga with Compensation

This demo intentionally fails payment when:

- card number ends with `0000`, or
- amount is greater than `1000`

Use this request:

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cust-202",
    "item": "premium-monitor",
    "amount": 1500,
    "card_number": "4000000000000000"
  }'
```

Then verify:

```bash
curl http://localhost:8001/orders
curl http://localhost:8002/payments
```

Expected result:

- order becomes `CANCELLED`
- payment becomes `FAILED`
- compensation event `ORDER_CANCELLED` is published

## Kafka Topics

The services create and use these topics:

- `order.created`
- `payment.requested`
- `payment.completed`
- `payment.failed`
- `order.cancelled`

## Inspect Kafka Messages

Open Kafka UI:

```text
http://localhost:8090
```

You can inspect topics and verify the event flow visually.

## Useful Commands

Show logs:

```bash
docker compose logs -f order-service
docker compose logs -f payment-service
docker compose logs -f kafka
```

List containers:

```bash
docker compose ps
```

Stop everything:

```bash
docker compose down
```

Stop and remove volumes too:

```bash
docker compose down -v
```

## Important Demo Rules

- No service is mapped to port `5000`
- Order Service is the **Saga Orchestrator**
- Payment Service is the **Saga Participant**
- Compensation is modeled as **order cancellation**
- SQLite is used only to keep the demo simple and self-contained

## Next Enhancements

If you want to evolve this demo further, add:

- inventory-service as another saga participant
- shipping-service as another participant
- idempotency keys
- outbox pattern
- retry / DLQ topics
- schema registry / Avro / Protobuf
- PostgreSQL instead of SQLite
