# Redis Caching Demo README

## Start the lab

```bash
docker compose up -d
```

## Check containers

```bash
docker ps
```

## Open Redis CLI

```bash
docker exec -it redis redis-cli
```

## Test commands

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

## View stats

```bash
docker exec -it redis redis-cli INFO memory
docker exec -it redis redis-cli INFO stats
docker exec -it redis redis-cli DBSIZE
```

## UI

Open:
- http://localhost:8081

## Optional Python demo

Create `app.py`:

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

Install dependency and run:

```bash
pip install redis
python3 app.py
```
