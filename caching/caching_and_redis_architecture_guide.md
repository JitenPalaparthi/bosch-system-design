# Caching Explained — Concepts, Redis Architecture, and Docker Compose Lab

## 1) What is caching?

**Caching** means storing frequently accessed or expensive-to-compute data in a faster layer so future requests can be served more quickly.

Instead of always going to the original source such as:

- database
- external API
- filesystem
- microservice
- computation engine

the application first checks a **cache**.

If the data exists in the cache, it is returned immediately.

---

## 2) Why caching is used

Caching is mainly used to improve:

- response time
- throughput
- database load
- application scalability
- user experience

### Example

Without cache:

```text
Client -> App -> Database -> App -> Client
```

With cache:

```text
Client -> App -> Cache -> App -> Client
                |
                +--> if miss -> Database -> Cache -> Client
```

---

## 3) Basic caching flow

```text
1. Client sends request
2. Application checks cache
3. If found => cache hit
4. If not found => cache miss
5. App reads from database / source
6. App stores result in cache
7. App returns response
```

---

## 4) Cache hit vs cache miss

### Cache hit
Requested data is already present in cache.

Benefits:
- very low latency
- reduced database load
- improved throughput

### Cache miss
Requested data is not in cache.

Then:
- application fetches from source
- stores it in cache
- returns it to client

---

## 5) Important caching terms

### A. TTL (Time To Live)
How long cached data remains valid.

Example:
- user profile cached for 5 minutes
- product catalog cached for 30 minutes

### B. Eviction
When cache is full, old or less useful data is removed.

Common policies:
- LRU = Least Recently Used
- LFU = Least Frequently Used
- FIFO = First In First Out
- random eviction

### C. Invalidation
Removing or updating stale cache data when the original data changes.

### D. Warm cache / cold cache
- **Cold cache**: cache is empty
- **Warm cache**: cache already contains commonly used data

---

## 6) Types of caching

## A. Application cache
Inside the application process.

Example:
- local in-memory maps
- in-process caches

Pros:
- extremely fast
- simple

Cons:
- each app instance has separate cache
- hard to share across replicas

---

## B. Distributed cache
External cache server shared by multiple application instances.

Example:
- Redis
- Memcached

Pros:
- shared across services
- consistent across replicas
- central cache layer

Cons:
- network hop required
- external component to operate

---

## C. Browser / CDN / edge cache
Used for:
- static content
- images
- HTML
- JS/CSS
- API edge responses

---

## 7) Common cache patterns

## A. Cache-aside (lazy loading)
Most common pattern.

Flow:

```text
App -> check cache
  if hit -> return
  if miss -> read DB -> put in cache -> return
```

### Advantages
- simple
- cache stores only what is needed
- flexible

### Disadvantages
- first request is slower
- stale data possible if invalidation is not handled properly

---

## B. Read-through cache
Application reads through cache layer directly. Cache itself fetches data from backend on miss.

---

## C. Write-through cache
Application writes to cache, and cache writes to DB immediately.

### Benefit
Cache and DB remain aligned more closely.

### Cost
Write path becomes more involved.

---

## D. Write-back / write-behind cache
Application writes to cache first. Cache writes to DB later asynchronously.

### Benefit
Fast writes

### Risk
Potential data loss if cache fails before persistence

---

## E. Refresh-ahead
Frequently used keys are refreshed before they expire.

---

## 8) Cache-aside architecture diagram

```text
                +------------------+
                |      Client      |
                +--------+---------+
                         |
                         v
                +------------------+
                |   Application    |
                +----+--------+----+
                     |        |
             cache hit|        | cache miss
                     v        v
               +---------+   +-----------+
               |  Redis  |   | Database  |
               +----+----+   +-----+-----+
                    ^              |
                    +--------------+
                     populate cache
```

---

## 9) Why Redis is popular for caching

Redis is widely used because it provides:

- in-memory speed
- rich data structures
- TTL support
- eviction policies
- replication
- persistence options
- pub/sub and streams
- clustering and high availability support

---

## 10) What is Redis?

**Redis** is an in-memory data structure store used for:

- cache
- session store
- distributed locks
- rate limiting
- queueing
- pub/sub
- counters
- leaderboards

It supports structures like:

- string
- hash
- list
- set
- sorted set
- bitmap
- stream

---

## 11) Redis basic architecture

### Single-node Redis

```text
          +---------------------+
          |    Application      |
          +----------+----------+
                     |
                     v
              +-------------+
              |   Redis     |
              | in-memory   |
              +------+------+ 
                     |
                     v
               disk persistence
                (optional AOF/RDB)
```

---

## 12) Redis caching behavior

When used as a cache:

- app stores key-value pairs in Redis
- app can set TTL
- app can delete key on data update
- Redis may evict keys if memory limit is reached

Example:

```text
key   = user:1001
value = JSON of user profile
ttl   = 300 seconds
```

---

## 13) Redis replication architecture

In Redis replication:

- one node is **primary**
- one or more nodes are **replicas**

Diagram:

```text
                 +------------------+
                 |   Application    |
                 +---------+--------+
                           |
                           v
                     +-----------+
                     |  Primary  |
                     |   Redis   |
                     +-----+-----+
                           |
              +------------+------------+
              |                         |
              v                         v
        +-----------+             +-----------+
        | Replica 1 |             | Replica 2 |
        +-----------+             +-----------+
```

### Usage
- writes usually go to primary
- replicas can be used for reads
- improves availability and scale for read-heavy workloads

---

## 14) Redis Sentinel architecture

Redis Sentinel provides:

- monitoring
- automatic failover
- primary discovery

Diagram:

```text
              +-----------------------+
              |      Application      |
              +-----------+-----------+
                          |
                          v
                  discovers primary
                          |
          +---------------+----------------+
          |        Sentinel nodes          |
          +---------------+----------------+
                          |
                          v
                    +-----------+
                    |  Primary  |
                    +-----+-----+
                          |
               +----------+----------+
               |                     |
               v                     v
         +-----------+         +-----------+
         | Replica 1 |         | Replica 2 |
         +-----------+         +-----------+
```

If primary fails, Sentinel elects a replica as the new primary.

---

## 15) Redis Cluster architecture

Redis Cluster is used for scaling Redis horizontally.

It supports:

- data partitioning using hash slots
- replication
- failover

Diagram:

```text
                   +------------------+
                   |   Application    |
                   +---------+--------+
                             |
                             v
                     +----------------+
                     | Redis Cluster  |
                     +----------------+
                        /      |      \
                       /       |       \
                      v        v        v
                 +--------+ +--------+ +--------+
                 |Master1 | |Master2 | |Master3 |
                 +---+----+ +---+----+ +---+----+
                     |          |          |
                     v          v          v
                 +--------+ +--------+ +--------+
                 |Replica | |Replica | |Replica |
                 +--------+ +--------+ +--------+
```

### Important concept
Redis Cluster splits keys across **16384 hash slots**.

Each master owns a subset of hash slots.

---

## 16) Redis persistence

Redis is in-memory, but it can also persist to disk.

### A. RDB
- periodic snapshot
- efficient for backups
- may lose recent writes between snapshots

### B. AOF
- append-only log of writes
- better durability
- larger disk usage

### C. Both together
Common in production depending on requirements

---

## 17) Cache invalidation strategies

Cache invalidation is one of the hardest parts.

Common approaches:

### A. TTL-based expiration
Let data expire automatically.

### B. Explicit invalidation
Delete cache key after updating DB.

Example:
- update user in DB
- delete `user:1001` from Redis

### C. Versioned keys
Instead of reusing same key, use a version.

Example:
- `product:100:v1`
- `product:100:v2`

---

## 18) Example Redis commands

Set a key:

```bash
redis-cli SET user:1001 '{"name":"JP","city":"Vijayawada"}'
```

Get a key:

```bash
redis-cli GET user:1001
```

Set key with TTL:

```bash
redis-cli SETEX user:1001 300 '{"name":"JP"}'
```

Check TTL:

```bash
redis-cli TTL user:1001
```

Delete a key:

```bash
redis-cli DEL user:1001
```

Increment a counter:

```bash
redis-cli INCR page:home:views
```

Use hash:

```bash
redis-cli HSET user:1001 name JP city Vijayawada
redis-cli HGETALL user:1001
```

---

## 19) When to use caching

Use caching when:

- data is read often
- data changes less frequently than it is read
- backend calls are expensive
- latency matters
- rate reduction on source system is needed

Examples:
- product catalog
- user profile
- session data
- configuration
- feature flags
- API responses
- leaderboard counters

---

## 20) When caching may not help much

Caching may be less useful when:

- data changes constantly
- every request is unique
- consistency must always be exact and immediate
- working set is much larger than cache memory
- invalidation overhead exceeds the benefit

---

## 21) Risks and trade-offs

Caching gives major benefits, but it also adds challenges:

- stale data
- cache stampede
- memory sizing issues
- eviction surprises
- cache consistency issues
- operational complexity in distributed setups

---

## 22) Cache stampede problem

A **cache stampede** happens when many requests try to rebuild the same expired key at once.

### Example
A hot key expires, then 10,000 requests hit DB at the same time.

### Mitigation
- request coalescing
- distributed locking
- refresh-ahead
- randomized TTL
- stale-while-revalidate patterns

---

## 23) Redis memory eviction policies

If Redis reaches configured memory limit, it can evict data using policies such as:

- `noeviction`
- `allkeys-lru`
- `volatile-lru`
- `allkeys-landom`
- `volatile-random`
- `allkeys-lfu`
- `volatile-lfu`

### Common choice for cache
- `allkeys-lru`
- `allkeys-lfu`

---

## 24) Simple end-to-end architecture with DB and Redis

```text
                +------------------+
                |      Client      |
                +--------+---------+
                         |
                         v
                +------------------+
                |    API Service    |
                +----+----------+---+
                     |          |
                     |          |
                     v          v
                +--------+   +--------+
                | Redis  |   |   DB   |
                +--------+   +--------+

Read path:
- API checks Redis
- on miss reads DB
- populates Redis

Write path:
- API writes DB
- API invalidates or updates Redis
```

---

## 25) Example: product cache

### Read flow
1. API receives `/products/101`
2. Check Redis key `product:101`
3. If found, return it
4. If not found, fetch from DB
5. Store in Redis with TTL
6. Return response

### Write flow
1. Update product in DB
2. Delete `product:101` from Redis
3. Next read repopulates cache

---

## 26) Docker Compose lab

This lab gives you:

- Redis server
- Redis Commander UI
- optional small Python app showing cache usage

### File: `docker-compose.yml`

```yaml
services:
  redis:
    image: redis:7.2
    container_name: redis
    command: >
      redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    networks:
      - redis-net

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: redis-commander
    environment:
      REDIS_HOSTS: local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    networks:
      - redis-net

networks:
  redis-net:

volumes:
  redisdata:
```

---

## 27) Start the lab

```bash
docker compose up -d
```

Then access:

- Redis server on port `6379`
- Redis Commander UI on `http://localhost:8081`

---

## 28) Test Redis locally

### Open Redis CLI inside container

```bash
docker exec -it redis redis-cli
```

### Example commands

```bash
SET app:message "hello redis"
GET app:message

SETEX user:1001 60 "cached-user"
TTL user:1001

HSET session:1 user JP role admin
HGETALL session:1

INCR counter:pageviews
GET counter:pageviews
```

---

## 29) Inspect memory and stats

```bash
docker exec -it redis redis-cli INFO memory
docker exec -it redis redis-cli INFO stats
docker exec -it redis redis-cli DBSIZE
```

---

## 30) Optional Python cache demo

### File: `app.py`

```python
import json
import time
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user(user_id: int):
    key = f"user:{user_id}"
    cached = r.get(key)

    if cached:
        print("CACHE HIT")
        return json.loads(cached)

    print("CACHE MISS -> simulating DB call")
    time.sleep(2)

    value = {"id": user_id, "name": "User-" + str(user_id)}
    r.setex(key, 60, json.dumps(value))
    return value

print(get_user(101))
print(get_user(101))
```

Run:

```bash
pip install redis
python3 app.py
```

You will see:
- first call slower because of miss
- second call fast because of hit

---

## 31) Redis architecture decision summary

### Single Redis
Use when:
- simple cache
- low operational complexity
- development or small production setup

### Redis + replica
Use when:
- read scaling needed
- better availability needed

### Redis + Sentinel
Use when:
- automatic failover required
- no sharding needed yet

### Redis Cluster
Use when:
- dataset is too large for one node
- horizontal scale is required
- high availability + partitioning needed

---

## 32) Best practices

- cache only useful hot data
- define TTL carefully
- use predictable key naming
- invalidate on writes
- monitor hit ratio
- watch memory usage
- choose eviction policy intentionally
- avoid storing unbounded large values
- protect against stampede for hot keys

---

## 33) Key naming examples

```text
user:1001
product:101
session:abcd1234
rate_limit:login:192.168.1.10
feature_flag:new_checkout
```

---

## 34) Summary

Caching improves system performance by keeping hot or expensive data in a faster layer.

Redis is popular because it gives:

- very fast in-memory access
- TTL support
- rich data structures
- replication
- persistence
- high availability and clustering options

For most applications, the most common pattern is:

- **cache-aside**
- **Redis as distributed cache**
- **DB as source of truth**
- **TTL + invalidation on write**

---
