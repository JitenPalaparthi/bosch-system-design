# Sharding in MongoDB — Explanation, Examples, Architecture Diagrams, and Docker Compose Lab

## 1) What is sharding?

**Sharding** is a horizontal scaling technique where data is split across multiple database nodes using a **shard key**.

Instead of storing the whole dataset in one MongoDB server, MongoDB distributes documents across multiple **shards**. Each shard stores only part of the total data.

### Why sharding is needed

When a single database server hits limits in:

- storage capacity
- write throughput
- read throughput
- CPU / memory
- maintenance window size

you scale **out** by adding more shards instead of only scaling **up**.

---

## 2) Core MongoDB sharded cluster components

A MongoDB sharded cluster has three major components:

1. **Shards**
   - Store the actual application data
   - In production, each shard is usually a **replica set**

2. **Config Servers**
   - Store cluster metadata
   - Keep information about chunks, shard locations, and cluster configuration

3. **mongos**
   - Query router
   - Applications connect to **mongos**, not directly to the shards

---

## 3) High-level architecture diagram

```text
                    +----------------------+
                    |   Application / API  |
                    +----------+-----------+
                               |
                               v
                        +-------------+
                        |   mongos    |
                        | Query Router|
                        +------+------+ 
                               |
                +--------------+--------------+
                |                             |
                v                             v
       +------------------+         +------------------+
       |  Config Server   |         |   Balancer /     |
       | Metadata (CSRS)  |         | chunk migration  |
       +------------------+         +------------------+

                +--------------+--------------+
                |                             |
                v                             v
         +-------------+               +-------------+
         |   Shard 1   |               |   Shard 2   |
         | mongod/RS   |               | mongod/RS   |
         +-------------+               +-------------+
                |                             |
                +-------------+---------------+
                              |
                              v
                       Distributed data
```

---

## 4) How MongoDB decides where data goes

MongoDB uses the **shard key** to decide which shard should store a document.

Example document:

```json
{
  "_id": 1,
  "customerId": 1001,
  "region": "south",
  "orderTotal": 2999
}
```

If `customerId` is the shard key, MongoDB uses that value to place the document into a **chunk**, and chunks are distributed across shards.

---

## 5) What are chunks?

MongoDB does not move single documents one by one for balancing. It groups data into **chunks**.

- A chunk is a range of shard key values
- Chunks are split as data grows
- The **balancer** moves chunks between shards to keep distribution even

### Chunk view

```text
Shard Key Range for customerId

Chunk 1:   1      -> 1000     -> Shard 1
Chunk 2:   1001   -> 2000     -> Shard 2
Chunk 3:   2001   -> 3000     -> Shard 1
Chunk 4:   3001   -> 4000     -> Shard 2
```

---

## 6) Routing behavior

### Targeted query
If the query includes the shard key, `mongos` can send the request only to the relevant shard.

Example:

```javascript
db.orders.find({ customerId: 1001 })
```

This is efficient because `mongos` can route it directly.

### Scatter-gather query
If the query does **not** include the shard key, `mongos` may need to query **all shards**.

Example:

```javascript
db.orders.find({ orderTotal: { $gt: 1000 } })
```

This is more expensive.

---

## 7) Range sharding vs hashed sharding

## A. Range-based sharding

Documents are grouped by contiguous shard key ranges.

Example shard key:
```javascript
{ customerId: 1 }
```

### Good for
- range queries
- ordered access
- date range lookups

### Risk
If inserts always increase, like timestamps or auto-increment style values, all new writes can go to one shard and create a **hot shard**.

Diagram:

```text
Range shard key: customerId

1------1000 | 1001------2000 | 2001------3000 | 3001------4000
   Shard 1         Shard 2          Shard 1          Shard 2
```

---

## B. Hashed sharding

MongoDB hashes the shard key value before distribution.

Example shard key:
```javascript
{ customerId: "hashed" }
```

### Good for
- even write distribution
- reducing hot spotting

### Limitation
Not ideal for range queries on the same field

Diagram:

```text
customerId values -> hash(customerId) -> distributed pseudo-randomly

1001 -> hash -> Shard 2
1002 -> hash -> Shard 1
1003 -> hash -> Shard 2
1004 -> hash -> Shard 1
```

---

## 8) Choosing a good shard key

A good shard key should ideally provide:

- **high cardinality**  
  Many distinct values

- **good distribution**  
  Avoid concentrating writes on one shard

- **query usefulness**  
  Frequently used in filters

### Bad shard key examples

- `status` with only values like `NEW`, `DONE`, `FAILED`
- `country` if most users are from one country
- monotonically increasing timestamps for heavy write workloads

### Better shard key examples

- `customerId`
- `tenantId`
- compound keys like `{ tenantId: 1, orderId: 1 }`
- hashed keys for high-ingest workloads

---

## 9) MongoDB example scenario

Suppose you have an `orders` collection:

```json
{
  "_id": 101,
  "tenantId": "t1",
  "customerId": 5001,
  "createdAt": "2026-04-19T08:00:00Z",
  "amount": 1200,
  "status": "PAID"
}
```

### Example 1: shard by customerId (hashed)

```javascript
sh.enableSharding("shop")

db = db.getSiblingDB("shop")

db.orders.createIndex({ customerId: "hashed" })

sh.shardCollection("shop.orders", { customerId: "hashed" })
```

### Why choose this?
- customer writes distribute more evenly
- reduces hot shard risk
- works well when most access is customer-centric

---

## 10) Example 2: shard by tenantId and orderId

For multi-tenant systems:

```javascript
db.orders.createIndex({ tenantId: 1, orderId: 1 })

sh.shardCollection("shop.orders", { tenantId: 1, orderId: 1 })
```

### Why choose this?
- tenant-based isolation
- queries filtered by tenant can be routed efficiently
- orderId adds cardinality inside each tenant

---

## 11) Insert and query examples

### Insert sample data

```javascript
use shop

db.orders.insertMany([
  { tenantId: "t1", customerId: 1001, orderId: 1, amount: 500, status: "PAID" },
  { tenantId: "t1", customerId: 1002, orderId: 2, amount: 900, status: "NEW" },
  { tenantId: "t2", customerId: 2001, orderId: 3, amount: 1200, status: "PAID" },
  { tenantId: "t2", customerId: 2002, orderId: 4, amount: 300, status: "FAILED" }
])
```

### Targeted query example

```javascript
db.orders.find({ customerId: 1001 })
```

### Scatter-gather style query example

```javascript
db.orders.find({ status: "PAID" })
```

If `status` is not part of the shard key and not otherwise targeted, the query may fan out.

---

## 12) Internal flow diagram for writes

```text
Client
  |
  v
mongos
  |
  +--> checks metadata from config servers
  |
  +--> computes target chunk from shard key
  |
  +--> routes write to correct shard
  |
  v
Shard receives write and stores document
```

---

## 13) Internal flow diagram for balancing

```text
Data grows
   |
   v
Chunk becomes too large
   |
   v
MongoDB splits chunk
   |
   v
Balancer checks shard distribution
   |
   v
Chunk migrated from busy shard to less loaded shard
```

---

## 14) Practical benefits of sharding

- horizontal scale for storage
- increased parallel write capacity
- increased aggregate read capacity
- better handling of very large collections
- isolation of load across multiple machines

---

## 15) Trade-offs and challenges

Sharding is powerful, but it adds complexity.

### Challenges

- shard key design is critical
- bad shard key can cause hot shards
- cross-shard aggregation may cost more
- operational complexity increases
- balancing and resharding can be resource intensive

---

## 16) When to shard

Shard when:

- your dataset is too large for one node
- one node cannot handle write volume
- one node cannot handle read volume
- future growth makes vertical scaling risky or too costly

Do **not** shard too early unless you have clear growth indicators or multi-tenant scale requirements.

---

## 17) Simple architecture diagram with two shards

```text
                    +---------------------+
                    |      Application    |
                    +----------+----------+
                               |
                               v
                         +-----------+
                         |  mongos   |
                         +-----+-----+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
      +---------------+                 +---------------+
      |    Shard 1    |                 |    Shard 2    |
      | orders chunk  |                 | orders chunk  |
      | 1..1000       |                 | 1001..2000    |
      +---------------+                 +---------------+

            Config servers store metadata about:
            - chunk ranges
            - shard mapping
            - cluster config
```

---

## 18) Production note

In production:

- config servers should be a **replica set**
- each shard should usually be a **replica set**
- clients connect only to **mongos**
- shard key selection should be tested with expected query patterns

---

## 19) Docker Compose lab (simple local sharded demo)

This lab is for **learning/demo only**, not production.

It uses:

- 1 config server
- 2 shard servers
- 1 mongos router

### File: `docker-compose.yml`

```yaml
services:
  configsvr:
    image: mongo:7.0
    container_name: configsvr
    command: >
      mongod --configsvr --replSet configReplSet --port 27019 --bind_ip_all
    ports:
      - "27019:27019"
    volumes:
      - configdb:/data/db
    networks:
      - mongo-shard-net

  shard1:
    image: mongo:7.0
    container_name: shard1
    command: >
      mongod --shardsvr --replSet shard1ReplSet --port 27018 --bind_ip_all
    ports:
      - "27018:27018"
    volumes:
      - shard1db:/data/db
    networks:
      - mongo-shard-net

  shard2:
    image: mongo:7.0
    container_name: shard2
    command: >
      mongod --shardsvr --replSet shard2ReplSet --port 27020 --bind_ip_all
    ports:
      - "27020:27020"
    volumes:
      - shard2db:/data/db
    networks:
      - mongo-shard-net

  mongos:
    image: mongo:7.0
    container_name: mongos
    depends_on:
      - configsvr
      - shard1
      - shard2
    command: >
      mongos --configdb configReplSet/configsvr:27019 --bind_ip_all --port 27017
    ports:
      - "27017:27017"
    networks:
      - mongo-shard-net

networks:
  mongo-shard-net:

volumes:
  configdb:
  shard1db:
  shard2db:
```

---

## 20) Bootstrap commands

Start the cluster:

```bash
docker compose up -d
```

Initialize replica sets:

### A. Initialize config server replica set

```bash
docker exec -it configsvr mongosh --port 27019 --eval '
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [{ _id: 0, host: "configsvr:27019" }]
})
'
```

### B. Initialize shard1 replica set

```bash
docker exec -it shard1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard1ReplSet",
  members: [{ _id: 0, host: "shard1:27018" }]
})
'
```

### C. Initialize shard2 replica set

```bash
docker exec -it shard2 mongosh --port 27020 --eval '
rs.initiate({
  _id: "shard2ReplSet",
  members: [{ _id: 0, host: "shard2:27020" }]
})
'
```

Wait a few seconds, then add shards through mongos:

```bash
docker exec -it mongos mongosh --port 27017 --eval '
sh.addShard("shard1ReplSet/shard1:27018");
sh.addShard("shard2ReplSet/shard2:27020");
sh.status();
'
```

---

## 21) Enable sharding and shard a collection

```bash
docker exec -it mongos mongosh --port 27017
```

Then inside `mongosh`:

```javascript
sh.enableSharding("shop")

db = db.getSiblingDB("shop")

db.orders.createIndex({ customerId: "hashed" })

sh.shardCollection("shop.orders", { customerId: "hashed" })

sh.status()
```

---

## 22) Insert test data

```javascript
for (let i = 1; i <= 1000; i++) {
  db.orders.insertOne({
    customerId: i,
    tenantId: "tenant-" + (i % 5),
    amount: Math.floor(Math.random() * 10000),
    status: (i % 2 === 0) ? "PAID" : "NEW"
  })
}
```

---

## 23) Check distribution

```javascript
db.orders.getShardDistribution()
```

You can also inspect cluster status:

```javascript
sh.status()
```

---

## 24) Example query patterns

### Good routed query
```javascript
db.orders.find({ customerId: 123 })
```

### Less targeted query
```javascript
db.orders.find({ status: "PAID" })
```

### Aggregation example
```javascript
db.orders.aggregate([
  { $match: { tenantId: "tenant-1" } },
  { $group: { _id: "$status", total: { $sum: "$amount" } } }
])
```

---

## 25) ASCII diagram for shard key hot-spot problem

### Bad case: increasing timestamp as shard key

```text
New inserts -----> always latest timestamp
                         |
                         v
                    mostly one shard gets new writes
```

### Better case: hashed customerId

```text
customerId -> hash -> spread across shards
writes distribute more evenly
```

---

## 26) Best practices

- choose shard key using real query patterns
- prefer high-cardinality keys
- avoid low-cardinality fields
- avoid monotonically increasing keys for heavy writes unless carefully designed
- test routed vs scatter-gather query behavior
- use replica sets for shards in production
- monitor chunk distribution and balancer activity

---

## 27) Summary

Sharding in MongoDB means:

- splitting data horizontally across shards
- routing queries through `mongos`
- storing metadata in config servers
- distributing data using a shard key
- balancing data using chunks and the balancer

A good shard key is the foundation of a successful sharded design.

---

## 28) Useful commands cheat sheet

```javascript
sh.status()
sh.enableSharding("shop")
sh.shardCollection("shop.orders", { customerId: "hashed" })
db.orders.getShardDistribution()
db.orders.createIndex({ customerId: "hashed" })
```

---

## 29) Important learning note

This Docker Compose lab is intentionally minimal for training. Real production deployments typically use:

- 3 config servers in a config server replica set
- replica sets for each shard
- multiple mongos routers
- authentication / keyfiles / TLS
- backup and monitoring

---
