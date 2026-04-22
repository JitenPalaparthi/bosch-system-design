# Chaos Engineering – Complete Guide

## 📌 What is Chaos Engineering?

Chaos Engineering is a disciplined approach to proactively testing system resilience by intentionally injecting failures into a system to observe behavior under stress.

Goal: Build confidence that the system can withstand unexpected disruptions.

---

## 🎯 Key Principles

1. Define steady state (latency, throughput, error rate)
2. Form hypothesis
3. Inject failures
4. Observe behavior
5. Minimize blast radius
6. Automate experiments

---

## 🧱 Types of Failures

- Infrastructure: VM crash, disk failure
- Network: latency, packet loss, partition
- Application: crashes, memory leaks
- Dependency: DB down, Kafka unavailable
- Resource: CPU/memory exhaustion

---

## 🏗️ Architecture Example

Client → Load Balancer → Services → DB/Cache

Chaos Injection Points:
- Kill service
- Add latency
- Drop packets
- Simulate DB failure

---

## 🚀 Use Cases

### Microservices
- Validate circuit breakers
- Test retries and fallback

### Kubernetes
- Kill pods
- Node failures

### Database Failover
- Kill primary DB
- Validate replica takeover

### Network Testing
- Simulate partitions

### Load Testing
- Combine traffic spikes + failures

---

## ⚙️ Tools

### Enterprise
- Chaos Monkey
- Gremlin
- AWS FIS
- Azure Chaos Studio

### Kubernetes
- LitmusChaos
- Chaos Mesh
- Kube-monkey

### Network
- Toxiproxy
- Pumba
- tc (Linux)

### Observability
- Prometheus
- Grafana
- Jaeger

---

## 🧪 Example Commands

kubectl delete pod <pod-name>
kubectl scale deployment my-app --replicas=0

---

## ⚠️ Best Practices

- Start in staging
- Small blast radius
- Have rollback plan
- Monitor metrics
- Automate

---

## 📊 Metrics

- Latency (p95, p99)
- Error rate
- Throughput
- Availability
- Recovery time

---

## 🔥 Summary

Chaos Engineering helps build:
- Resilient systems
- Fault-tolerant architectures
- High availability systems

