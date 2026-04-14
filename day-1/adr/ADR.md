# 📘 Architecture Decision Records (ADR) – Complete Guide

---

## 🖼️ ADR Overview

![ADR Intro](adr-1.png)

![ADR Format](adr-2.png)

![ADR Benefits](adr-3.png)

![ADR Detailed](adr-4.png)

![ADR Example](adr-5.png)

---

<details open>
<summary><strong>🔹 What is an ADR?</strong></summary>

### Definition
ADR (Architecture Decision Record) is a **document that captures important architectural decisions** along with their context and consequences.

### Why ADR?
- Avoid tribal knowledge
- Maintain decision history
- Improve team alignment

### Key Idea
> Every important decision should be **documented, justified, and traceable**

</details>

---

<details open>
<summary><strong>🔹 ADR Structure</strong></summary>

### Standard Format

1. **Context**
2. **Decision**
3. **Alternatives**
4. **Consequences**
5. **Status**
6. **Date**

---

### Explanation

#### Context
- Problem statement
- Constraints (scale, latency, cost)

#### Decision
- Final chosen approach

#### Alternatives
- Other options considered

#### Consequences
- Trade-offs, risks, benefits

#### Status
- Proposed / Accepted / Deprecated

#### Date
- Decision timestamp

</details>

---

<details open>
<summary><strong>🔹 Benefits of ADR</strong></summary>

- 📄 Clear documentation
- 👥 Knowledge sharing
- 🕒 Historical tracking
- 🔁 Avoid repeated mistakes
- 📈 Better system evolution

</details>

---

# 🧩 Real ADR Examples

---

<details open>
<summary><strong>📌 ADR-001: Kubernetes Ingress vs API Gateway</strong></summary>

### Context
Need external access to microservices deployed in Kubernetes.

### Decision
Use **API Gateway (e.g., Kong / AWS API Gateway)** instead of basic Ingress.

### Alternatives
- Kubernetes Ingress (NGINX)
- Service Mesh (Istio Gateway)

### Consequences

**Pros:**
- Centralized auth, rate limiting
- Better observability

**Cons:**
- Extra cost
- Added latency

### Status
Accepted

### Date
2026-04-13

</details>

---

<details>
<summary><strong>📌 ADR-002: Database Choice (PostgreSQL vs NoSQL)</strong></summary>

### Context
System requires strong consistency for financial transactions.

### Decision
Use **PostgreSQL (RDBMS)**

### Alternatives
- MongoDB
- Cassandra

### Consequences

**Pros:**
- ACID compliance
- Strong consistency

**Cons:**
- Harder horizontal scaling

### Status
Accepted

</details>

---

<details>
<summary><strong>📌 ADR-003: Synchronous vs Asynchronous Communication</strong></summary>

### Context
Services experiencing latency spikes due to blocking calls.

### Decision
Adopt **event-driven architecture (Kafka)**

### Alternatives
- REST synchronous calls
- gRPC

### Consequences

**Pros:**
- Loose coupling
- Better scalability

**Cons:**
- Increased complexity
- Eventual consistency

### Status
Accepted

</details>

---

# 🧠 Best Practices

<details open>
<summary><strong>Click to expand</strong></summary>

- Keep ADRs **short and precise**
- One decision per ADR
- Store in **Git repository**
- Use numbering (ADR-001, ADR-002)
- Update status instead of deleting

</details>

---

# 📌 Final Insight

> "Good architecture is not just about decisions, but about remembering *why* decisions were made."

