# Active-Active vs Active-Passive Architecture (System Design Perspective)

---

## 📌 Overview

In distributed systems, **Active-Active** and **Active-Passive** are two fundamental patterns for:
- High Availability
- Disaster Recovery
- Load Distribution

These patterns apply to:
- Databases
- Microservices
- Kafka / Messaging systems
- Storage systems
- Entire regions (multi-region architectures)

---

# 1. Active-Passive Architecture

## 📌 Definition
- One system is **ACTIVE (primary)** → serves traffic
- Another system is **PASSIVE (standby)** → does not serve traffic until failover

---

## 🧩 Architecture Diagram

```
        +-----------+
        |  Clients  |
        +-----+-----+
              |
              v
        +-----+-----+
        |  Primary  |
        |  (Active) |
        +-----+-----+
              |
         Replication
              |
        +-----v-----+
        | Secondary |
        | (Passive) |
        +-----------+
```

---

## ⚙️ Characteristics

| Aspect | Active-Passive |
|-------|---------------|
| Traffic | Only active handles traffic |
| Failover | Required |
| RTO | Medium |
| RPO | Low (depends on replication) |
| Cost | Lower |
| Complexity | Lower |

---

## 🧠 Database Example

### PostgreSQL (Primary-Replica)

- Primary DB handles:
  - Writes
  - Reads

- Replica DB:
  - Receives WAL logs (replication)
  - Used for failover

### Failover Flow

1. Primary crashes
2. Replica promoted to primary
3. Application switches DB endpoint

---

## 🧠 System Example

### E-commerce (Single Region DR)

- Region A → Active
- Region B → Passive

Flow:
- All traffic → Region A
- Region B is standby
- On failure → DNS switch to Region B

---

## ⚠️ Challenges

- Failover time (downtime)
- Data lag (if async replication)
- Manual/automated promotion complexity
- Cold standby may not be ready instantly

---

# 2. Active-Active Architecture

## 📌 Definition
- Multiple systems are **ACTIVE simultaneously**
- All nodes handle traffic

---

## 🧩 Architecture Diagram

```
              +-------------------+
              |     Clients       |
              +--------+----------+
                       |
              +--------v----------+
              | Global Load Balancer |
              +--------+----------+
                       |
         +-------------+-------------+
         |                           |
+--------v--------+        +---------v--------+
| Region A        |        | Region B         |
| Active          |        | Active           |
+--------+--------+        +---------+--------+
         |                           |
         +------------ Sync ---------+
```

---

## ⚙️ Characteristics

| Aspect | Active-Active |
|-------|--------------|
| Traffic | Distributed |
| Failover | Automatic |
| RTO | Near zero |
| RPO | Near zero |
| Cost | High |
| Complexity | Very high |

---

## 🧠 Database Example

### Multi-Master Database

Examples:
- Cassandra
- CockroachDB
- DynamoDB (internally)

### Behavior

- Writes can go to any region
- Data replicated across regions
- Conflict resolution required

---

## ⚠️ Conflict Example

Two regions update same record:

- Region A → price = 100
- Region B → price = 120

Conflict resolution strategies:
- Last Write Wins
- Vector clocks
- CRDTs

---

## 🧠 System Example

### Global E-commerce

- India users → Region India
- US users → Region US

Both regions:
- Accept writes
- Serve reads
- Sync data via Kafka

---

# 3. Hybrid Patterns

## 3.1 Active-Active for App + Active-Passive DB

```
App: Active-Active
DB: Active-Passive
```

Used when:
- DB does not support multi-master

---

## 3.2 Active-Passive with Read Replicas

```
Primary → Writes
Replicas → Reads
```

---

# 4. Kafka Example

## Active-Passive

- Cluster A → Active
- Cluster B → Mirror (MirrorMaker)

Failover:
- Switch producers/consumers

## Active-Active

- Multi-cluster Kafka
- Bi-directional replication
- Complex offset management

---

# 5. Storage Example

## Active-Passive
- Primary S3 bucket
- Backup in another region

## Active-Active
- Multi-region object storage
- Read/write anywhere

---

# 6. Comparison Summary

| Feature | Active-Passive | Active-Active |
|--------|--------------|--------------|
| Availability | High | Very High |
| Downtime | Possible | Minimal |
| Cost | Lower | Higher |
| Complexity | Low | High |
| Data Consistency | Strong | Eventual |
| Failover | Required | Automatic |

---

# 7. When to Use What?

## Use Active-Passive when:
- Simpler systems
- Strong consistency required
- Budget constraints
- Easier operations needed

## Use Active-Active when:
- Global applications
- Ultra-low latency needed
- High availability critical
- Can handle eventual consistency

---

# 8. Real-World Mapping

| System | Pattern |
|------|--------|
| Banking Core DB | Active-Passive |
| Payment Gateways | Active-Active |
| Kafka Streaming | Hybrid |
| CDN | Active-Active |
| Internal Tools | Active-Passive |

---

# 9. Key Design Decisions

- Consistency vs Availability (CAP)
- Conflict resolution strategy
- Replication latency
- Failover automation
- Cost vs resilience

---

# 10. Final Insight

> Active-Passive = Simplicity + Reliability  
> Active-Active = Scalability + Complexity

---

