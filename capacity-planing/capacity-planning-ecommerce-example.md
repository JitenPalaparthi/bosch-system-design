# Capacity Planning – E-commerce Microservices (Concrete Example)

## 📌 Scenario

Design capacity planning for a large-scale e-commerce system (Flipkart/Amazon-like).

### Assumptions
- 10 million users/day
- 20 requests/user/day
- Total requests/day = 200 million
- Peak multiplier = 10x
- Avg response size = 300 KB
- Avg request size = 10 KB

---

## 📊 Traffic Calculation

### Average RPS
200,000,000 / 86,400 ≈ 2315 RPS

### Peak RPS
2315 × 10 ≈ 23,150 RPS

---

## 🧱 Architecture Overview

```
Users
  |
CDN / WAF
  |
Global Load Balancer
  |
API Gateway
  |
+-----------------------------+
| Microservices Layer         |
| (User, Order, Payment etc)  |
+-------------+---------------+
              |
     +--------+--------+
     |                 |
   Cache           Kafka
     |                 |
     +--------+--------+
              |
           Database
              |
        Object Storage
```

---

# 1. Compute Planning

### Assume:
- 1 instance handles 500 RPS

Instances needed:
23,150 / 500 ≈ 46 instances

Add 30% headroom:
≈ 60 instances

### CPU Calculation
- CPU per request = 8 ms

Total CPU/sec:
23,150 × 0.008 = 185 CPU sec/sec

≈ 185 vCPUs needed

Add headroom:
≈ 240 vCPUs total

---

# 2. Memory Planning

### Assume:
- 1.5 GB per instance

Total memory:
60 × 1.5 GB = 90 GB

Add headroom:
≈ 120 GB

---

# 3. Storage Planning

## 3.1 Database

### Orders Data
- 5 million orders/day
- 3 KB per order

Daily:
15 GB/day

Monthly:
450 GB

Yearly:
5.4 TB

Add indexes (70%):
≈ 9.2 TB

Replication (2x):
≈ 18 TB

---

## 3.2 Logs

- 150 GB/day logs
- 30-day retention

≈ 4.5 TB hot logs

Archive (180 days):
≈ 27 TB

---

## 3.3 Object Storage

- Product images + uploads
- 2 TB/day

Monthly:
≈ 60 TB

---

# 4. Network Planning

### Peak Bandwidth

23,150 RPS × 300 KB ≈ 6.9 GB/sec

≈ 55 Gbps

Add overhead:
≈ 70 Gbps

---

# 5. Cache Planning

### Assume:
- 10 million hot items
- 5 KB each

Cache:
≈ 50 GB

Add overhead:
≈ 70 GB Redis cluster

---

# 6. Kafka Planning

### Assume:
- 100K events/sec
- 1 KB/event

Per day:
≈ 8.6 TB

7-day retention:
≈ 60 TB

Replication factor 3:
≈ 180 TB

---

# 7. Final Capacity Summary

| Component | Capacity |
|----------|---------|
| App Instances | 60 |
| CPU | 240 vCPU |
| Memory | 120 GB |
| DB Storage | 18 TB |
| Logs (Hot) | 4.5 TB |
| Logs (Archive) | 27 TB |
| Object Storage | 60 TB/month |
| Cache | 70 GB |
| Kafka | 180 TB |
| Network | 70 Gbps |

---

# 8. Architecture Diagram (Detailed)

```
               +----------------------+
               |       Users          |
               +----------+-----------+
                          |
                +---------v----------+
                | CDN / WAF          |
                +---------+----------+
                          |
                +---------v----------+
                | Global LB          |
                +---------+----------+
                          |
                +---------v----------+
                | API Gateway        |
                +---------+----------+
                          |
        +-----------------+-----------------+
        |                                   |
        v                                   v
+-------------------+            +-------------------+
| App Cluster       |            | Worker Cluster    |
| 60 instances      |            | async processing  |
+---------+---------+            +---------+---------+
          |                                |
          +----------+----------+----------+
                     |          |
                     v          v
              +----------+   +----------+
              |  Redis   |   |  Kafka   |
              +-----+----+   +-----+----+
                    |              |
                    +------+-------+
                           |
                           v
                    +-------------+
                    | Database    |
                    +------+------+ 
                           |
                           v
                    +-------------+
                    | Object Store|
                    +-------------+
```

---

# 9. Key Insights

- Network becomes the biggest bottleneck at scale
- Storage grows exponentially (logs + Kafka + objects)
- Compute is easier to scale than database
- Cache is critical for performance
- Kafka storage dominates in event-driven systems

---

# 10. Final Thought

> Capacity planning is not about guessing numbers — it is about understanding system behavior under stress.

