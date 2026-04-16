# 📘 etcd (Raft) Cluster using Docker Compose

---

## 🧠 Overview

This document demonstrates how to run a **3-node etcd cluster** using Docker Compose to understand **Raft consensus in practice**.

---

## 📦 docker-compose.yml

```yaml
version: "3.8"

services:
  etcd1:
    image: quay.io/coreos/etcd:v3.5.9
    container_name: etcd1
    command: >
      /usr/local/bin/etcd
      --name etcd1
      --data-dir /etcd-data
      --initial-advertise-peer-urls http://etcd1:2380
      --listen-peer-urls http://0.0.0.0:2380
      --listen-client-urls http://0.0.0.0:2379
      --advertise-client-urls http://etcd1:2379
      --initial-cluster etcd1=http://etcd1:2380,etcd2=http://etcd2:2380,etcd3=http://etcd3:2380
      --initial-cluster-state new
      --initial-cluster-token etcd-cluster-1
    ports:
      - "2379:2379"
    networks:
      - etcd-net

  etcd2:
    image: quay.io/coreos/etcd:v3.5.9
    container_name: etcd2
    command: >
      /usr/local/bin/etcd
      --name etcd2
      --data-dir /etcd-data
      --initial-advertise-peer-urls http://etcd2:2380
      --listen-peer-urls http://0.0.0.0:2380
      --listen-client-urls http://0.0.0.0:2379
      --advertise-client-urls http://etcd2:2379
      --initial-cluster etcd1=http://etcd1:2380,etcd2=http://etcd2:2380,etcd3=http://etcd3:2380
      --initial-cluster-state new
      --initial-cluster-token etcd-cluster-1
    networks:
      - etcd-net

  etcd3:
    image: quay.io/coreos/etcd:v3.5.9
    container_name: etcd3
    command: >
      /usr/local/bin/etcd
      --name etcd3
      --data-dir /etcd-data
      --initial-advertise-peer-urls http://etcd3:2380
      --listen-peer-urls http://0.0.0.0:2380
      --listen-client-urls http://0.0.0.0:2379
      --advertise-client-urls http://etcd3:2379
      --initial-cluster etcd1=http://etcd1:2380,etcd2=http://etcd2:2380,etcd3=http://etcd3:2380
      --initial-cluster-state new
      --initial-cluster-token etcd-cluster-1
    networks:
      - etcd-net

networks:
  etcd-net:
```

---

## ▶️ Start Cluster

```bash
docker-compose up -d
```

---

## 🔍 Check Cluster Status

```bash
docker exec -it etcd1 etcdctl \
  --endpoints=http://etcd1:2379,http://etcd2:2379,http://etcd3:2379 \
  endpoint status --write-out=table
```

---

## 🧪 Put / Get Example

```bash
docker exec -it etcd1 etcdctl put name "Jiten"
docker exec -it etcd2 etcdctl get name
docker exec -it etcd2 etcdctl get "" --prefix --keys-only=false
```

---

## ⚠️ Simulate Failure

```bash
docker stop etcd1
```

Then:

```bash
docker exec -it etcd2 etcdctl endpoint status --write-out=table
```

---

## 🧠 Raft Mapping

| Action | Raft Concept |
|--------|-------------|
| Start cluster | Leader election |
| put key | Log replication |
| majority ack | Commit |
| stop node | Failure handling |
| new leader | Re-election |

---

## 📌 Key Insight

> etcd uses Raft to ensure strong consistency using majority quorum.
