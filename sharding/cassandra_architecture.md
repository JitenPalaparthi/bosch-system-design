# Apache Cassandra Architecture & Data Distribution (Sharding)

## 1. Overview

Apache Cassandra is a **distributed, decentralized NoSQL database** designed for:
- High availability
- Linear scalability
- Fault tolerance
- No single point of failure

Unlike MongoDB, Cassandra uses **automatic sharding (partitioning)** and **replication by design**.

---

## 2. Core Architecture

```
          +----------------------+
          |     Application      |
          +----------+-----------+
                     |
                     v
        +---------------------------+
        |     Cassandra Cluster     |
        +---------------------------+
         |      |        |        |
         v      v        v        v
       Node1  Node2    Node3    Node4
```

### Key Points
- All nodes are **equal (peer-to-peer)**
- No master / slave (leaderless architecture)
- Any node can accept read/write requests

---

## 3. Data Distribution (Sharding in Cassandra)

Cassandra automatically distributes data using **partitioning (sharding)**.

### How it works
```
Hash(partition_key) → Token → Node
```

### Diagram
```
Data (Partition Key)
        |
     Hashing
        |
     Token Ring
        |
+--------+--------+--------+--------+
| Node1  | Node2  | Node3  | Node4  |
+--------+--------+--------+--------+
```

### Key Concepts
- Partition Key → determines data placement
- Consistent Hashing → distributes data evenly
- Token Ring → logical structure of nodes

---

## 4. Replication in Cassandra

Cassandra replicates data across multiple nodes.

### Replication Factor (RF)
- RF = 3 → data stored in 3 nodes

### Diagram
```
Write Request
     |
     v
Coordinator Node
     |
     +----> Node1 (Replica)
     +----> Node2 (Replica)
     +----> Node3 (Replica)
```

### Replication Strategies
- SimpleStrategy → single data center
- NetworkTopologyStrategy → multi-DC

---

## 5. Write Path

```
Client → Coordinator Node
        → Commit Log (durability)
        → Memtable (memory)
        → SSTable (disk flush)
```

### Key Points
- Writes are fast (append-only)
- No locking
- Tunable consistency

---

## 6. Read Path

```
Client → Coordinator
        → Query replicas
        → Merge results
        → Return data
```

### Optimization Techniques
- Bloom filters
- Caching
- Compaction

---

## 7. Consistency Levels

Cassandra provides **tunable consistency**.

| Level | Description |
|------|-------------|
| ONE | One replica response |
| QUORUM | Majority of replicas |
| ALL | All replicas |

### Formula
```
R + W > RF  → Strong Consistency
```

---

## 8. Gossip Protocol

Used for node communication.

```
Node1 <--> Node2 <--> Node3 <--> Node4
```

### Purpose
- Node discovery
- Failure detection
- State sharing

---

## 9. Failure Handling

- No single point of failure
- Automatic replication ensures availability
- Hinted handoff for temporary failures
- Read repair for consistency

---

## 10. Comparison with MongoDB

| Feature | Cassandra | MongoDB |
|--------|----------|---------|
| Architecture | Peer-to-peer | Primary-secondary |
| Sharding | Automatic | Manual |
| Replication | Built-in | Replica sets |
| Scaling | Linear | Requires sharding |
| Consistency | Tunable | Strong by default |

---

## 11. When to Use Cassandra

Use Cassandra when:
- Massive write throughput is needed
- Data is distributed globally
- High availability is critical
- Event/time-series data

Avoid when:
- Strong ACID transactions needed
- Complex joins required

---

## 12. Summary

- Cassandra = **Leaderless distributed DB**
- Uses **consistent hashing for sharding**
- Uses **replication for fault tolerance**
- Provides **tunable consistency**
- Ideal for **large-scale distributed systems**

