# Capacity Planning from an Architecture Perspective

## Overview

Capacity planning is the process of estimating and provisioning the **right amount of resources** so a system can meet:
- performance targets
- availability goals
- growth expectations
- cost constraints

From an architecture perspective, capacity planning is not only about “how many servers” are needed. It also includes:
- **compute sizing**
- **memory sizing**
- **storage sizing**
- **network throughput**
- **database throughput**
- **cache efficiency**
- **resilience under peak load**
- **future growth planning**

---

# 1. Core Goals of Capacity Planning

A good capacity plan answers:

1. How much traffic will the system handle?
2. What is the expected peak load?
3. How many compute nodes are needed?
4. How much memory is required?
5. How much storage is needed today and after growth?
6. How much network bandwidth is required?
7. Where are the bottlenecks?
8. What is the failover capacity?
9. What is the cost of over-provisioning vs under-provisioning?

---

# 2. Key Terms

| Term | Meaning |
|---|---|
| Throughput | Number of requests/events processed per second |
| Latency | Time taken to process one request |
| Concurrency | Number of simultaneous active users or requests |
| QPS/RPS | Queries/Requests per second |
| CPU Utilization | Percentage of CPU in use |
| Memory Utilization | Percentage of RAM in use |
| IOPS | Input/output operations per second |
| Bandwidth | Volume of data transferred per second |
| Headroom | Extra reserved capacity for spikes/failures |
| SLA/SLO | Service commitments for uptime and latency |

---

# 3. Capacity Planning Layers in Architecture

Capacity planning must be done across all architectural layers.

## 3.1 Client Layer
- Daily active users
- Concurrent active users
- Request frequency per user
- Peak-hour multiplier
- Geography and time-zone spikes

## 3.2 Edge / Network Layer
- CDN traffic
- Load balancer capacity
- TLS termination overhead
- API gateway throughput
- Internet/region bandwidth

## 3.3 Application / Compute Layer
- CPU per request
- Memory per process/pod
- Thread/goroutine/worker usage
- Autoscaling thresholds
- Background job capacity

## 3.4 Data Layer
- Database reads/writes
- Connection pool usage
- Storage growth
- IOPS requirements
- Replication overhead

## 3.5 Cache Layer
- Hit ratio
- Memory footprint
- Eviction policy
- Hot key risk

## 3.6 Messaging / Streaming Layer
- Event rate
- Partition count
- Consumer lag
- Retention storage
- Replication cost

## 3.7 Reliability Layer
- Failover capacity
- multi-AZ / multi-region reserve
- disaster recovery capacity
- N+1 planning

---

# 4. High-Level Architecture Diagram

```text
                        +-------------------+
                        |      Clients      |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        |   CDN / WAF / LB  |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        |   API Gateway     |
                        +---------+---------+
                                  |
                +-----------------+-----------------+
                |                                   |
                v                                   v
      +-------------------+               +-------------------+
      |  App Service A    |               |  App Service B    |
      +---------+---------+               +---------+---------+
                |                                   |
                +-----------------+-----------------+
                                  |
                   +--------------+--------------+
                   |                             |
                   v                             v
          +-------------------+         +-------------------+
          |      Cache        |         |   Message Queue   |
          |   Redis/Memcached |         | Kafka/RabbitMQ    |
          +---------+---------+         +---------+---------+
                    |                             |
                    +--------------+--------------+
                                   |
                                   v
                        +-------------------+
                        |    Database       |
                        | SQL / NoSQL       |
                        +---------+---------+
                                  |
                                  v
                        +-------------------+
                        | Object / Block    |
                        |    Storage        |
                        +-------------------+
```

---

# 5. Workload Characterization

Before sizing anything, define the workload.

## 5.1 Traffic Questions
- How many users per day?
- How many concurrent users?
- What is the peak-hour traffic?
- Are there flash sales or burst events?
- Are reads much higher than writes?
- What is the average payload size?

## 5.2 Example Inputs

Assume:
- 5,000,000 users/day
- 10 page/API calls per user/day
- Total requests/day = 50,000,000
- Peak multiplier = 8x average
- Average response size = 200 KB
- Average request size = 5 KB

### Average RPS

```text
Average RPS = Total requests per day / 86400
Average RPS = 50,000,000 / 86,400 ≈ 579 RPS
```

### Peak RPS

```text
Peak RPS = Average RPS × Peak multiplier
Peak RPS = 579 × 8 ≈ 4,632 RPS
```

This peak number becomes the baseline for sizing.

---

# 6. Compute Capacity Planning

Compute planning is primarily about:
- CPU cores
- number of instances/pods
- worker parallelism
- autoscaling limits

## 6.1 Compute Sizing Formula

A practical approximation:

```text
Required compute instances = Peak RPS / RPS per instance
```

If one application instance handles 250 RPS safely:

```text
Instances needed = 4,632 / 250 ≈ 18.5
```

Round up:
- 19 instances minimum
- add headroom (say 30%)

```text
19 × 1.3 ≈ 25 instances
```

So architecturally:
- **baseline steady state**: 25 app instances
- maybe spread across **3 AZs**
- roughly **8 + 8 + 9**

## 6.2 CPU-Based Method

If profiling shows:
- one request consumes **12 ms CPU time**
- peak RPS = 4,632

Then required CPU seconds per second:

```text
CPU seconds/sec = RPS × CPU time per request
CPU seconds/sec = 4,632 × 0.012 = 55.58 CPU seconds/sec
```

That means approximately:

```text
~56 vCPUs needed
```

With 30% headroom:

```text
56 × 1.3 ≈ 73 vCPUs
```

So plan around **72 to 80 vCPUs** total.

## 6.3 Compute Architecture Concerns
- Keep services stateless for horizontal scaling
- Separate read-heavy and write-heavy services
- Isolate CPU-heavy jobs from request-serving services
- Use async processing for long-running tasks
- Keep autoscaling warm enough to absorb sudden spikes

---

# 7. Memory Capacity Planning

Memory planning depends on:
- application runtime footprint
- connection pools
- cache usage
- in-flight requests
- JVM/GC behavior if applicable
- container/pod limits

## 7.1 App Memory Formula

```text
Total memory = (memory per instance) × (number of instances)
```

If each instance needs:
- base process memory = 800 MB
- overhead + buffers = 300 MB
- safe memory = 1.2 GB/instance

For 25 instances:

```text
25 × 1.2 GB = 30 GB
```

Add operational headroom:
- reserve around **36–40 GB total app memory**

## 7.2 Memory Considerations
- Python, Java, Node, Go all behave differently
- Large connection pools increase RAM
- In-memory queues and caches can dominate memory usage
- Memory leaks distort planning
- GC pauses can appear as CPU or latency issues

---

# 8. Storage Capacity Planning

Storage planning includes:
- primary database storage
- indexes
- logs
- backups
- object/blob storage
- message retention
- DR copies
- growth over time

## 8.1 Types of Storage

### Block Storage
Used for:
- databases
- VM disks
- persistent volumes

### Object Storage
Used for:
- backups
- images
- videos
- logs
- archival data

### File Storage
Used for:
- shared files
- reports
- content management

---

## 8.2 Database Storage Planning

Suppose:
- 10 million new records/month
- average row size = 2 KB
- indexes add 70%
- replication factor = 2 copies total
- retain 24 months online

### Raw data per month

```text
10,000,000 × 2 KB = 20 GB/month
```

### With indexes

```text
20 GB × 1.7 = 34 GB/month
```

### For 24 months

```text
34 GB × 24 = 816 GB
```

### With replication (2 copies)

```text
816 GB × 2 = 1,632 GB
```

So DB storage planning should consider roughly:

- **1.6 TB primary + replica footprint**
- plus free space for compaction, vacuum, temp files, migrations

A safer architecture plan:
- allocate **2 to 2.5 TB effective DB storage**

---

## 8.3 Log Storage Planning

Assume:
- application logs = 40 GB/day
- security/audit logs = 15 GB/day
- infrastructure logs = 20 GB/day
- total = 75 GB/day
- retain hot for 14 days
- archive for 180 days

### Hot log storage

```text
75 GB/day × 14 = 1,050 GB
```

### Archive storage

```text
75 GB/day × 180 = 13,500 GB = 13.5 TB
```

So log architecture may require:
- **~1 TB hot searchable storage**
- **~13.5 TB cold object storage**

---

## 8.4 Object Storage Planning

Suppose user uploads:
- 500,000 files/day
- average file size = 1.5 MB

```text
Daily object storage = 500,000 × 1.5 MB = 750,000 MB ≈ 732 GB/day
```

Monthly:

```text
732 GB × 30 ≈ 21.5 TB/month
```

Annual:

```text
21.5 TB × 12 ≈ 258 TB/year
```

This is why object storage and lifecycle policies are critical.

---

## 8.5 Backup Storage Planning

For a 2 TB production database:
- daily incremental backups
- weekly full backup
- monthly archive snapshot

Example:
- weekly full backup = 2 TB
- daily incremental average = 120 GB/day
- keep 4 full backups and 30 incrementals

```text
Full backups = 2 TB × 4 = 8 TB
Incrementals = 120 GB × 30 = 3.6 TB
Total backup storage ≈ 11.6 TB
```

With cross-region copies:
- effectively double it

```text
11.6 TB × 2 = 23.2 TB
```

---

# 9. Network Capacity Planning

Network planning often gets ignored, but it matters at scale.

## 9.1 Bandwidth Formula

```text
Bandwidth = RPS × average payload size
```

If:
- peak RPS = 4,632
- average response = 200 KB

```text
4,632 × 200 KB = 926,400 KB/s ≈ 904 MB/s
```

In bits:

```text
904 MB/s × 8 ≈ 7.2 Gbps
```

Add request payloads, retries, overhead, TLS, replication:
- real requirement may be **9–12 Gbps**

## 9.2 East-West vs North-South Traffic

### North-South
Traffic between users and the system.

### East-West
Traffic between services, caches, databases, and queues.

East-west traffic can exceed user-facing traffic in microservices architectures.

---

# 10. Database Capacity Planning

Database capacity is not just about size. It is also about:
- writes/sec
- reads/sec
- active connections
- locking/contention
- IOPS
- replication lag
- query complexity

## 10.1 Example DB Sizing

Suppose:
- writes = 800/sec
- reads = 5,000/sec
- average query time = 8 ms
- peak connections = 2,000

Architecture options:
- primary for writes
- 2 or more read replicas
- connection pooling
- query/index tuning
- cache for hot reads

## 10.2 Database Diagram

```text
                  +--------------------+
                  |   Application      |
                  +---------+----------+
                            |
                 +----------+----------+
                 | Connection Pooler   |
                 +----------+----------+
                            |
                 +----------+----------+
                 |   Primary DB        |
                 |  (writes + reads)   |
                 +----------+----------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
     +-------------------+       +-------------------+
     | Read Replica 1    |       | Read Replica 2    |
     +-------------------+       +-------------------+
```

---

# 11. Cache Capacity Planning

Cache planning improves performance and reduces DB cost.

## 11.1 Cache Questions
- What is the hit rate?
- How many hot keys exist?
- How large are cached objects?
- What TTL is used?
- What is the eviction pattern?

## 11.2 Cache Size Formula

```text
Cache size = number of hot objects × average object size
```

If:
- 5 million hot objects
- average cached item = 4 KB

```text
5,000,000 × 4 KB = 20,000,000 KB ≈ 19 GB
```

With overhead, metadata, fragmentation:
- plan for **28–32 GB cache memory**

---

# 12. Messaging and Streaming Capacity Planning

For Kafka or similar systems, plan for:
- events/sec
- partitions
- retention time
- replication factor
- consumer lag
- storage growth

## 12.1 Example Kafka Storage

Suppose:
- 50,000 events/sec
- average event size = 1 KB
- retention = 7 days
- replication factor = 3

Per second:

```text
50,000 × 1 KB = 50 MB/s
```

Per day:

```text
50 MB/s × 86,400 ≈ 4.32 TB/day
```

For 7 days:

```text
4.32 TB × 7 = 30.24 TB
```

With replication factor 3:

```text
30.24 TB × 3 = 90.72 TB
```

So storage planning for the stream cluster needs roughly **91 TB**.

---

# 13. End-to-End Consolidated Capacity Example

Assume an internet-scale application with:

- 5,000,000 users/day
- peak 4,632 RPS
- app instance capacity = 250 RPS
- memory per app instance = 1.2 GB
- DB online storage = 2 TB effective planned
- logs = 75 GB/day
- object uploads = 732 GB/day
- Kafka retained storage = 91 TB
- target headroom = 30%

## 13.1 Overall Summary Table

| Layer | Estimate |
|---|---|
| App Instances | 25 |
| Total vCPU | 72–80 vCPU |
| App Memory | 36–40 GB |
| DB Storage | 2–2.5 TB |
| Hot Log Storage | ~1 TB |
| Archive Log Storage | ~13.5 TB |
| Backup Storage with cross-region | ~23 TB |
| Object Storage | ~21.5 TB/month |
| Network Bandwidth | ~9–12 Gbps |
| Kafka Storage | ~91 TB |

---

# 14. Capacity Planning Diagram with Compute, Storage, and Network

```text
                              +----------------------+
                              |       Clients        |
                              +----------+-----------+
                                         |
                                         v
                              +----------------------+
                              |   CDN / LB / WAF     |
                              |  Network Capacity    |
                              |   9-12 Gbps target   |
                              +----------+-----------+
                                         |
                                         v
                              +----------------------+
                              |    API Gateway       |
                              +----------+-----------+
                                         |
                      +------------------+------------------+
                      |                                     |
                      v                                     v
          +------------------------+           +------------------------+
          |   App Cluster          |           |   Worker Cluster       |
          | 25 instances           |           | async jobs / consumers |
          | 72-80 vCPU             |           | separate compute pool  |
          | 36-40 GB RAM           |           +-----------+------------+
          +-----------+------------+                       |
                      |                                    |
            +---------+---------+                          |
            |                   |                          |
            v                   v                          v
+---------------------+   +---------------------+   +---------------------+
|     Redis Cache     |   |   Primary DB        |   |   Kafka Cluster     |
| ~28-32 GB RAM       |   | 2-2.5 TB storage    |   | ~91 TB storage      |
+----------+----------+   +----------+----------+   +----------+----------+
           |                         |                         |
           |                         v                         |
           |              +---------------------+              |
           |              | Read Replicas       |              |
           |              +----------+----------+              |
           |                         |                         |
           +-------------------------+-------------------------+
                                     |
                                     v
                        +-----------------------------+
                        | Object / Backup / Log Store |
                        | 21.5 TB/month objects       |
                        | 13.5 TB archived logs       |
                        | 23 TB backup storage        |
                        +-----------------------------+
```

---

# 15. Headroom and Failure Planning

A good capacity plan is incomplete without failure assumptions.

## 15.1 Headroom Rules
Typical planning:
- keep 20–40% spare compute headroom
- reserve memory for spikes and failover
- keep storage below safe utilization thresholds
- never run DB storage near 100%
- plan for one-node or one-AZ loss

## 15.2 N+1 and N+2
- **N** = minimum needed
- **N+1** = one extra unit for failure
- **N+2** = two extra units for stronger resilience

If 19 instances are minimally needed:
- production target may be 25
- this supports headroom, rolling deploys, and single-node failure

---

# 16. Autoscaling Considerations

Autoscaling is not a replacement for planning.

Use autoscaling for:
- normal traffic variation
- day-night patterns
- burst absorption

But also define:
- minimum replica count
- maximum replica count
- cooldown intervals
- warm pool / pre-scaled nodes
- database limits
- queue lag thresholds

---

# 17. Common Bottlenecks

Typical bottlenecks include:
- CPU saturation
- memory leaks
- database write contention
- slow queries
- insufficient IOPS
- cache miss storms
- network bandwidth saturation
- hot partitions in Kafka
- too many DB connections
- oversized logs or backups

---

# 18. Trade-offs

| Dimension | Under-Provisioned | Over-Provisioned |
|---|---|---|
| Cost | Lower initially | Higher |
| Latency | Poor | Better |
| Reliability | Risky | Safer |
| Efficiency | High on paper, unstable in reality | Lower efficiency, more stable |
| Scaling | Reactive and painful | Easier |

---

# 19. Best Practices

1. Measure real traffic, do not guess blindly
2. Use peak load, not average load, for sizing
3. Add explicit headroom
4. Separate compute from storage planning
5. Size storage for growth, backups, and replication
6. Treat network as a first-class capacity concern
7. Use caching to offload databases
8. Benchmark before final sizing
9. Revisit the plan regularly
10. Capacity plan for failures, not only normal days

---

# 20. Final Summary

From an architecture perspective, overall capacity planning must combine:

- **compute capacity**
  - CPU
  - pods/instances
  - worker pools

- **memory capacity**
  - per-service RAM
  - cache RAM
  - connection overhead

- **storage capacity**
  - database growth
  - logs
  - backups
  - object storage
  - streaming retention

- **network capacity**
  - ingress
  - egress
  - east-west traffic
  - replication traffic

- **resilience capacity**
  - failover reserve
  - multi-AZ headroom
  - disaster recovery copies

The real architectural goal is:

> Build a system that survives peak load, failure events, growth, and operational change without violating performance or availability targets.

---

# 21. Quick Reference Formula Sheet

## Traffic
```text
Average RPS = total requests per day / 86400
Peak RPS = average RPS × peak multiplier
```

## Compute
```text
Instances = peak RPS / RPS per instance
Total CPU = peak RPS × CPU time per request
```

## Memory
```text
Total memory = memory per instance × number of instances
```

## Storage
```text
Data growth = records × average size
Effective DB size = raw data + indexes + replicas + free space
```

## Logs
```text
Log storage = log volume per day × retention days
```

## Backups
```text
Backup storage = full backups + incremental backups + cross-region copy
```

## Network
```text
Bandwidth = RPS × payload size
```

## Cache
```text
Cache size = hot objects × average object size
```

## Streaming
```text
Stream storage = events/sec × event size × retention × replication factor
```
