- Check Stats

echo stat | nc localhost 2181
echo stat | nc localhost 2182
echo stat | nc localhost 2183

- Create Topic
docker exec -it kafka1 kafka-topics \
  --create \
  --topic orders \
  --bootstrap-server kafka1:29092 \
  --partitions 1 \
  --replication-factor 1

- Produce

  docker exec -it kafka1 kafka-console-producer \
  --topic orders \
  --bootstrap-server kafka1:29092

- Consume

  docker exec -it kafka1 kafka-console-consumer \
  --topic orders \
  --from-beginning \
  --bootstrap-server kafka1:29092

- Very small failure demo

1. Find the ZooKeeper leader

echo stat | nc localhost 2181
echo stat | nc localhost 2182
echo stat | nc localhost 2183

2. Stop the leader container

    - stop only the leader

docker stop zk2 

3. Re-run stat

