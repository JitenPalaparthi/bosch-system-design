# Real-World Cost Breakdown (CDN, Kafka, DB, Compute at Scale)

## 1. Overview

This document provides a practical FinOps-oriented cost breakdown for large-scale distributed systems similar to Netflix/Uber.

Assumptions:
- 1M daily active users
- 100K concurrent users peak
- Multi-region deployment

---

## 2. CDN Cost (Content Delivery)

### Usage
- Video/images delivery
- Edge caching

### Cost Drivers
- Data transfer out (per GB)
- Requests (per 10K requests)

### Example Estimate
- 1 PB/month data transfer
- Cost ≈ $0.02/GB

Total:
= 1,000,000 GB × $0.02 ≈ $20,000/month

### Optimization
- Cache hit ratio > 90%
- Use regional edge caching

---

## 3. Kafka (Streaming Layer)

### Usage
- Event streaming
- Logs, analytics, pipelines

### Cost Drivers
- Broker instances
- Storage (retention)
- Network I/O

### Example Setup
- 6 brokers (m5.large equivalent)
- $150/month each

Compute:
= 6 × 150 = $900/month

Storage:
- 10 TB @ $0.10/GB ≈ $1,000/month

Total Kafka:
≈ $2,000/month

---

## 4. Database Cost (OLTP)

### Usage
- User data, transactions

### Cost Drivers
- Instance size
- Replication
- Storage

### Example Setup
- Primary + 2 replicas
- $500/month each

Compute:
= 3 × 500 = $1,500/month

Storage:
- 5 TB @ $0.12/GB ≈ $600/month

Total DB:
≈ $2,100/month

---

## 5. Compute (Microservices / Kubernetes)

### Usage
- API services
- Backend processing

### Cost Drivers
- Number of pods
- CPU/Memory usage
- Auto-scaling

### Example
- 50 nodes @ $100/month

Total:
= $5,000/month

---

## 6. Cache Layer (Redis)

### Usage
- Reduce DB load
- Fast access

### Example
- 3 nodes cluster
- $200/month each

Total:
= $600/month

---

## 7. Observability (Logs, Metrics, Traces)

### Usage
- Monitoring system health

### Cost Drivers
- Log volume
- Retention

Example:
- 5 TB logs/month @ $0.10/GB

Total:
≈ $500/month

---

## 8. Total Monthly Cost (Sample)

| Component   | Cost |
|------------|------|
| CDN        | $20,000 |
| Kafka      | $2,000 |
| Database   | $2,100 |
| Compute    | $5,000 |
| Cache      | $600 |
| Observability | $500 |

### Total ≈ $30,200/month

---

## 9. Key Insights

- CDN dominates cost at scale
- Compute is second biggest
- Kafka + DB relatively smaller but critical
- Logs can silently grow cost

---

## 10. Optimization Strategies

### CDN
- Increase cache hit ratio
- Compress content

### Kafka
- Reduce retention
- Optimize partitions

### DB
- Use read replicas efficiently
- Archive old data

### Compute
- Auto-scale aggressively
- Use spot instances

### Observability
- Log sampling
- Reduce retention

---

## 11. Advanced FinOps Thinking

Always evaluate:
- Cost per request
- Cost per user
- Cost per GB

---

## 12. Conclusion

At scale:
- Small inefficiencies → millions in cost
- Architecture decisions directly impact finances

Design systems with:
Performance + Reliability + Cost optimization
