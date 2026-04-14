# 📘 Failure Models in Distributed Systems

---

## 🖼️ Failure Models Comparison

![Failure Models](failure-model-1.png)

---

<details>
<summary>🔹 Network Failure (Click to expand)</summary>

### Definition
Failure in communication between services while services are alive.

### Scope
- Service-to-service communication
- Cross-node / cross-region

### Examples
- Packet loss
- Timeout
- Network partition

### Symptoms
- High latency
- Retry storms
- Partial failures

### Impact
- Cascading failures
- Resource exhaustion

### Mitigation
- Exponential backoff retries
- Circuit breakers
- Timeouts
- Bulkheads

</details>

---

<details>
<summary>🔹 Process Failure (Click to expand)</summary>

![Process Failure](failure-model-2.png)

### Definition
Failure of a single service instance or container.

### Examples
- Crash
- OOM
- Deadlock

### Symptoms
- Service down
- Health checks failing

### Impact
- Partial outage
- Request loss

### Mitigation
- Restart policies
- Replication
- Health checks
- Auto scaling

</details>

---

<details>
<summary>🔹 Region Failure (Click to expand)</summary>

![Region Failure](failure-model-3.png)

### Definition
Failure of an entire region or data center.

### Examples
- AWS outage
- Power failure

### Symptoms
- Complete system unavailable

### Impact
- Full outage
- Data loss risk

### Mitigation
- Multi-region deployment
- Failover strategies
- Disaster recovery
- DNS routing

</details>

---

## 🔄 Failure Interaction

<details>
<summary>Click to expand</summary>

- Network issue → retries increase  
- Retries → load spike  
- Load spike → process crashes  
- Multiple crashes → regional outage  

</details>

---

## ⚖️ CAP Mapping

<details>
<summary>Click to expand</summary>

- Network Failure → Partition  
- Process Failure → Availability  
- Region Failure → Availability + Partition  

</details>

---

## 📌 Final Thought

> Distributed systems fail not if, but when.

