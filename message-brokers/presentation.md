Kafka Architecture
------------------

https://docs.google.com/presentation/d/1HznwxAXAT9LtSgWcL3IF1XZLxnXQGp5lCCK4ZA7T-ZA/edit?usp=sharing

docker exec -it kafka bash

kafka-topics --bootstrap-server kafka:9092 --create --topic orders --partitions 3

kafka-console-produce --bootstrap-server kafka:9092 --topic orders

kafka-console-consume --bootstrap-server kafka:9092 --topic orders
