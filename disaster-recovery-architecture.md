# Disaster Recovery (DR) – Architecture Perspective

## Overview
Disaster Recovery (DR) is an architectural discipline ensuring systems recover from failures with minimal downtime and data loss.

---

## DR Strategy Levels

| Stage | Strategy | RTO | RPO |
|------|--------|-----|-----|
| Stage 0 | Backup & Restore | High | High |
| Stage 1 | Pilot Light | Medium | Medium |
| Stage 2 | Warm Standby | Low | Low |
| Stage 3 | Active-Active | Near Zero | Near Zero |

---

## Architecture Layers

### Infrastructure Layer
- Multi-region deployment
- Kubernetes / VMs
- Terraform / Ansible

### Network Layer
- DNS failover
- Global load balancing

### Application Layer
- Stateless services
- Idempotent APIs

### Data Layer
- Replication (sync/async)
- CDC pipelines

### Observability Layer
- Prometheus, Grafana
- Logs, alerts

---

## Stage 0: Backup & Restore

- No DR infra
- Restore from backups

```
Users → Primary → Backup Storage
```

---

## Stage 1: Pilot Light

- Minimal DR running
- Scale on failure

```
Primary → Replication → DR (Minimal)
```

---

## Stage 2: Warm Standby

- Fully running DR at reduced capacity

```
Users → Load Balancer → Primary
                         ↓
                     DR Region
```

---

## Stage 3: Active-Active

- Multi-region active systems

```
Users → Global LB → Region A
                    Region B
```

---

## Data Strategies

### Synchronous Replication
- Strong consistency

### Asynchronous Replication
- Eventual consistency

### CDC Pipeline
```
Postgres → Debezium → Kafka → OpenSearch
```

---

## Traffic Management

- DNS failover
- Geo load balancing
- Service mesh (Envoy/Istio)

---

## Distributed Patterns

- Stateless services
- CQRS
- Circuit breaker
- Bulkhead isolation

---

## Metrics

- RTO: Recovery time
- RPO: Data loss tolerance
- MTTR: Repair time

---

## Testing

- Chaos testing
- Failover drills
- Backup validation

---

## Summary

- DR evolves from simple to complex
- Trade-off: cost vs availability
- Design for failure
