
# Bottleneck Diagnostics — System Design

## 🧠 Overview

A **bottleneck** is any component that limits system throughput or increases latency.

> System performance is dictated by the slowest component in the request path.

This document provides a **production-grade framework** to:
- Identify bottlenecks
- Measure them
- Fix them systematically

---

# 🔍 1. Types of Bottlenecks

## 1. Compute Bottleneck
- CPU saturation
- Thread starvation

## 2. Memory Bottleneck
- High GC pauses
- Memory leaks
- Cache misses

## 3. Disk / I/O Bottleneck
- Slow reads/writes
- Disk queue buildup

## 4. Network Bottleneck
- High latency
- Packet loss
- Bandwidth limits

## 5. Database Bottleneck
- Slow queries
- Lock contention
- Connection exhaustion

## 6. Application Bottleneck
- Inefficient algorithms
- Blocking calls
- Poor concurrency handling

## 7. External Dependency Bottleneck
- Third-party APIs
- Payment gateways
- Auth providers

---

# 🧱 2. Bottleneck Identification Strategy

## Step 1: Define SLI
- Latency (p50, p95, p99)
- Throughput (RPS)
- Error rate

## Step 2: Trace Request Path
Break system into:

Client → CDN → LB → API → Services → DB → Cache → External APIs

## Step 3: Measure Each Layer
Use:
- Metrics
- Logs
- Traces

---

# 📊 3. Key Metrics to Track

## Latency
- p50 → typical
- p95 → slow requests
- p99 → tail latency

## Throughput
- Requests per second (RPS)

## Resource Usage
- CPU %
- Memory %
- Disk I/O
- Network I/O

## Queue Metrics
- Queue depth
- Processing delay

---

# 🔬 4. Diagnostic Techniques

## 1. Vertical Analysis (Layer by Layer)
Check:
- API latency
- DB latency
- Cache hit/miss
- External API time

## 2. Horizontal Analysis (Load Based)
Increase load gradually:
- Observe when system degrades

## 3. Flame Graphs
Identify:
- CPU hotspots
- Blocking calls

## 4. Distributed Tracing
Find:
- Slow services
- Call dependencies

---

# 🔥 5. Common Bottleneck Patterns

## 1. Database Hotspot
Symptoms:
- High query time
- Lock waits

Fix:
- Indexing
- Query optimization
- Read replicas

---

## 2. Cache Miss Storm
Symptoms:
- Sudden DB spike

Fix:
- Cache warming
- TTL tuning

---

## 3. Thread Pool Exhaustion
Symptoms:
- Requests queued
- High latency

Fix:
- Increase pool
- Async processing

---

## 4. Network Saturation
Symptoms:
- High latency
- Packet drops

Fix:
- Compression
- CDN
- Edge caching

---

## 5. N+1 Query Problem
Symptoms:
- Many DB calls per request

Fix:
- Join queries
- Batch fetching

---

# ⚙️ 6. Bottleneck Removal Strategies

## Scale Up (Vertical)
- Increase CPU/RAM

## Scale Out (Horizontal)
- Add replicas
- Load balancing

## Caching
- Redis / in-memory

## Asynchronous Processing
- Message queues

## Sharding
- Split data across nodes

## Rate Limiting
- Protect system

---

# 🧠 7. Advanced Concepts

## Amdahl’s Law
Optimizing non-bottleneck parts gives minimal improvement.

## Little’s Law
L = λ × W  
Queue size = throughput × latency

## Backpressure
System slows producers when consumers are overloaded.

---

# 📈 8. Real Example (E-commerce)

Problem:
- Checkout latency high

Diagnosis:
- Trace shows DB query slow

Root Cause:
- Missing index

Fix:
- Add index → latency drops from 2s → 200ms

---

# 🧩 9. End-to-End Diagnostic Flow

1. Detect issue (alert)
2. Check SLI (latency spike)
3. Use tracing → find slow service
4. Drill into DB / CPU / network
5. Identify root cause
6. Apply fix
7. Validate improvement

---

# ⚠️ 10. Anti-Patterns

- Guessing without metrics
- Optimizing everything blindly
- Ignoring tail latency
- Over-scaling without root cause

---

# 🧠 Final Mental Model

> Bottleneck = slowest component in system

To fix:
- Measure
- Identify
- Optimize only that part

---

# 🚀 Conclusion

Bottleneck diagnostics is about:
- Observability
- Systematic analysis
- Targeted optimization

Not guesswork.

A good engineer:
- Finds bottleneck quickly
- Fixes with minimal change
- Validates with metrics
