
Tools: 

Sidecar/Service Mesh
DAPR
ENVOY
ISTIO

GATEWAY:
Nginx
Kong
APISIX
APISeven
Trafik

Calling A from Another Service
-----------------------------
Orachastration
Choreography
Sync and Async

-- 
Dead Lock Queue
Backpressure
Jitter


etcd  (3 node)   --> key, value
kafka    --> leader follower/replication
postgres --> active / passive (patroni, haproxy --> active- passive)
mongodb (3 node cluster)--> shards , if enable replication = 2
cassandra --> distributed system

redis -- key,value

    client (sdks)
       |     
       |
------------------
Node1 Node2 Node3
