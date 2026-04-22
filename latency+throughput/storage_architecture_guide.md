# Storage Architecture Guide (HDD vs NVMe vs Distributed Storage)

## 1. HDD-Based Storage Architecture

```
Application
   ↓
Filesystem (EXT4/XFS)
   ↓
Block Layer (IO Scheduler)
   ↓
Disk Controller
   ↓
HDD (Spinning Disk)
```

### Characteristics

| Feature | Value |
|--------|------|
| Latency | 5–15 ms |
| IOPS | Low |
| Throughput | Medium |
| Cost | Low |

### Bottlenecks
- Mechanical seek time
- Rotational delay

---

## 2. NVMe / SSD Storage Architecture

```
Application
   ↓
Filesystem
   ↓
NVMe Driver
   ↓
PCIe Bus
   ↓
NVMe Controller
   ↓
Flash (NAND)
```

### Key Features
- Parallel queues (64K queues)
- Very low latency

### Characteristics

| Feature | Value |
|--------|------|
| Latency | 10–100 µs |
| IOPS | Very High |
| Throughput | Very High |
| Cost | High |

---

## 3. Distributed Storage Architecture (Ceph / HDFS / S3)

```
            +------------------+
            |     Client       |
            +--------+---------+
                     |
        ----------------------------
        |         Network          |
        ----------------------------
           |       |       |
       +---+---+ +---+---+ +---+---+
       | Node1 | | Node2 | | Node3 |
       | Disk  | | Disk  | | Disk  |
       +---+---+ +---+---+ +---+---+
            \        |        /
        Replication / Sharding
```

### Concepts

| Concept | Description |
|--------|------------|
| Replication | Data copied across nodes |
| Sharding | Data split across nodes |
| Consistency | Eventual / Strong |

### Characteristics

| Feature | Value |
|--------|------|
| Latency | Medium (network) |
| Throughput | High (aggregate) |
| Scalability | High |
| Reliability | High |

---

## Comparison Summary

| Feature | HDD | NVMe | Distributed |
|--------|-----|------|-------------|
| Latency | High | Very Low | Medium |
| IOPS | Low | Very High | Scalable |
| Cost | Low | High | Medium |
| Scalability | Low | Medium | High |

---

## Architecture Pattern (Tiered Storage)

```
Hot Data   → NVMe
Warm Data  → SSD
Cold Data  → HDD
Archive    → Object Storage (S3)
```

---

## When to Use What

### HDD
- Backup
- Archive
- Cost-sensitive workloads

### NVMe
- Databases
- Kafka
- Low-latency systems

### Distributed Storage
- Big Data
- Cloud-native systems
- Fault-tolerant architectures

---

## Notes

- Always measure using fio for realistic performance
- Focus on p99 latency, not averages
- Combine storage types for optimal cost/performance
