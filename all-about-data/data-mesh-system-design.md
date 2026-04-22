# Data Mesh in System Design

## 🧠 Overview
Data Mesh is a decentralized data architecture paradigm where data ownership is distributed across domain teams. Each domain treats its data as a product.

---

## 🏗️ Architecture
Self-serve platform + domain-owned data products.

Domains:
- Orders
- Payments
- Users
- Inventory

Each domain:
- Owns DB
- Publishes data
- Maintains pipelines

---

## 🔑 Principles
1. Domain Ownership  
2. Data as a Product  
3. Self-Serve Platform  
4. Federated Governance  

---

## 🛠️ Tools
- Kafka (Streaming)
- Debezium (CDC)
- Spark/Flink (Processing)
- S3 (Storage)
- Presto (Query)
- Airflow (Orchestration)
- DataHub (Catalog)

---

## 🔄 Flow
1. DB → Debezium  
2. Debezium → Kafka  
3. Kafka → Processing  
4. Processing → Storage  
5. Query via Presto  

---

## ⚖️ Pros
- Scalable
- Faster delivery
- Domain ownership

## ❌ Cons
- Complex governance
- Requires maturity

---

## 🧩 Conclusion
Data Mesh = Microservices for Data
