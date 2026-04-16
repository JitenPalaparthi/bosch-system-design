# NGINX Gateway Demo with Load Balancing (2 Replicas per Service)

This version extends the earlier gateway demo by adding **load balancing**.

## What changes here?

Instead of one container per service, we run:

- 2 replicas of `user-service`
- 2 replicas of `order-service`

NGINX sits in front and distributes traffic across replicas.

---

## Architecture

```text
                         +--------------------+
Client ----------------->|    NGINX Gateway   |
                         +---------+----------+
                                   |
                 +-----------------+-----------------+
                 |                                   |
                 v                                   v
          +-------------+                     +-------------+
          | user-svc-1  |                     | order-svc-1 |
          +-------------+                     +-------------+
          | user-svc-2  |                     | order-svc-2 |
          +-------------+                     +-------------+
```

NGINX uses **upstream blocks** to balance requests between replicas.

---

## Pattern demonstrated

### Gateway pattern
- Single public entry point
- Centralized routing
- Services remain internal

### Load balancing pattern
- One logical service has multiple instances
- Requests are spread across them
- Improves availability and throughput

---

## Important Docker Compose note

Plain `docker compose` does not automatically create multiple routable service endpoints for a single service name in a way that classic NGINX upstream config can always target directly.

So in this demo we define **explicit service containers**:

- `user-service-1`
- `user-service-2`
- `order-service-1`
- `order-service-2`

That makes the demo stable and easy to explain.

---

## Files

- `docker-compose.yml`
- `nginx/nginx.conf`
- `services/user_service/app.py`
- `services/order_service/app.py`

---

## Run

```bash
docker compose up --build
```

---

## Test users endpoint multiple times

```bash
curl http://localhost:8080/users
curl http://localhost:8080/users
curl http://localhost:8080/users
curl http://localhost:8080/users
```

You should see alternating responses from:
- `user-service-1`
- `user-service-2`

---

## Test orders endpoint multiple times

```bash
curl http://localhost:8080/orders
curl http://localhost:8080/orders
curl http://localhost:8080/orders
curl http://localhost:8080/orders
```

You should see alternating responses from:
- `order-service-1`
- `order-service-2`

---

## Health

```bash
curl http://localhost:8080/health
```

---

## Example behavior

### Users
One request may return:

```json
{
  "service": "user-service",
  "instance": "user-service-1",
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

Next request may return:

```json
{
  "service": "user-service",
  "instance": "user-service-2",
  "users": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

That shows load balancing is happening.

---

## How NGINX balances

In `nginx.conf`:

```nginx
upstream user_backend {
    server user-service-1:5001;
    server user-service-2:5001;
}
```

```nginx
upstream order_backend {
    server order-service-1:5002;
    server order-service-2:5002;
}
```

By default, NGINX uses **round robin**.

That means:
- request 1 -> instance 1
- request 2 -> instance 2
- request 3 -> instance 1
- request 4 -> instance 2

---

## Teaching explanation

### Without load balancing
If only one service instance exists:
- all traffic hits one backend
- no redundancy
- lower scalability

### With load balancing
Traffic is shared:
- better throughput
- better resilience
- easier horizontal scaling

---

## Stop

```bash
docker compose down
```

---

## Summary

This demo now shows both:

- **API Gateway** using NGINX
- **Load balancing** across 2 replicas per backend service
