# MongoDB Sharding Demo Commands

## Start
```bash
docker compose up -d
```

## Initialize config server replica set
```bash
docker exec -it configsvr mongosh --port 27019 --eval '
rs.initiate({
  _id: "configReplSet",
  configsvr: true,
  members: [{ _id: 0, host: "configsvr:27019" }]
})
'
```

## Initialize shard1 replica set
```bash
docker exec -it shard1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard1ReplSet",
  members: [{ _id: 0, host: "shard1:27018" }]
})
'
```

## Initialize shard2 replica set
```bash
docker exec -it shard2 mongosh --port 27020 --eval '
rs.initiate({
  _id: "shard2ReplSet",
  members: [{ _id: 0, host: "shard2:27020" }]
})
'
```

## Add shards to mongos
```bash
docker exec -it mongos mongosh --port 27017 --eval '
sh.addShard("shard1ReplSet/shard1:27018");
sh.addShard("shard2ReplSet/shard2:27020");
sh.status();
'
```

## Open mongos shell
```bash
docker exec -it mongos mongosh --port 27017
```

## Enable sharding and shard collection
```javascript
sh.enableSharding("shop")

db = db.getSiblingDB("shop")

db.orders.createIndex({ customerId: "hashed" })
sh.shardCollection("shop.orders", { customerId: "hashed" })
sh.status()
```

## Insert sample documents
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

## Check shard distribution
```javascript
db.orders.getShardDistribution()
```
