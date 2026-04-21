# MongoDB Architecture: Replication vs Sharding

## 1. Replication Architecture

Replication provides **high availability** and **failover**.

### Diagram
```
Application
   |
MongoDB Driver (replicaSet=rs0)
   |
   +-----------------------------+
   |             |               |
Primary      Secondary      Secondary
(Writes)     (Replica)      (Replica)

Replication via Oplog
```

### Key Points
- Primary handles all writes
- Secondaries replicate via oplog
- Automatic failover using elections
- Optional arbiter (no data)

---

## 2. Sharding Architecture

Sharding provides **horizontal scaling**.

### Diagram
```
Application
   |
 mongos (Query Router)
   |
   +----------+----------+----------+
   |          |          |
Shard1     Shard2     Shard3
(Replica)  (Replica)  (Replica)

   |
Config Server Replica Set (Metadata)
```

### Key Components
- mongos → query router
- Config servers → metadata storage
- Shards → store subset of data

---

## 3. Combined Architecture (Production)

```
Application
   |
 mongos Router
   |
   +----------+----------+----------+
   |          |          |
Shard1     Shard2     Shard3
(P+S+S)    (P+S+S)    (P+S+S)

   |
Config Server Replica Set
```

---

## 4. Replication vs Sharding

| Feature | Replication | Sharding |
|--------|------------|----------|
| Goal | High Availability | Scaling |
| Data | Full copy | Partitioned |
| Writes | Primary only | Routed to shard |
| Reads | Secondary possible | Distributed |
| Failover | Yes | Per shard |

---

## 5. Data Flow

### Replica Set
```
App → Primary → Oplog → Secondaries
```

### Sharded Cluster
```
App → mongos → Shard
```

---

## 6. Summary

- Replication = same data copied
- Sharding = data split
- Production = Sharding + Replication
