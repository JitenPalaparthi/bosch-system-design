
# Lambda vs Kappa Architecture — System Design + Patterns

## 🧠 Overview

Both **Lambda** and **Kappa** architectures are designed for large-scale data processing.

- **Lambda Architecture** → Batch + Stream processing
- **Kappa Architecture** → Stream-only processing

---

# 🏗️ Lambda Architecture

## Core Idea
Combine:
- Batch processing (accuracy)
- Stream processing (low latency)

## Architecture

```
Data Source
   |
   v
Ingestion Layer
   |
   +----------------------+
   |                      |
   v                      v
Batch Layer          Speed Layer
   |                      |
Batch Views        Real-time Views
   \                     /
    \                   /
     ------> Serving Layer ---->
                  |
                  v
             Applications
```

---

## Components

### 1. Batch Layer
- Stores full dataset
- Recomputes results

### 2. Speed Layer
- Processes real-time data

### 3. Serving Layer
- Combines outputs

---

## Pros
- High accuracy
- Fault tolerant

## Cons
- Complex
- Duplicate logic

---

# ⚡ Kappa Architecture

## Core Idea
Use only streaming for everything.

## Architecture

```
Data Source
   |
   v
Kafka (Log Storage)
   |
   v
Stream Processing
   |
   v
Serving DB
   |
   v
Applications
```

---

## Components

### 1. Streaming Layer
- Processes all data

### 2. Log Storage
- Kafka retains data

### 3. Serving Layer
- Query processed data

---

## Pros
- Simple
- No duplicate logic

## Cons
- Replay cost
- Strong streaming infra required

---

# ⚖️ Comparison

| Feature | Lambda | Kappa |
|--------|--------|-------|
| Processing | Batch + Stream | Stream only |
| Complexity | High | Low |
| Latency | Medium | Low |
| Maintenance | Hard | Easy |
| Reprocessing | Batch recompute | Stream replay |

---

# 🧩 Architecture Patterns

## 1. Event-Driven Pattern
- Producers emit events
- Consumers process asynchronously

Used in:
- Both Lambda & Kappa

---

## 2. CQRS Pattern
- Write → Database
- Read → Optimized views

Lambda:
- Batch views + real-time views

Kappa:
- Stream-generated views

---

## 3. Data Pipeline Pattern

Stages:
1. Ingestion
2. Processing
3. Storage
4. Query

Lambda:
- Dual pipelines

Kappa:
- Single streaming pipeline

---

## 4. Replay Pattern

Kappa relies heavily on:
- Event replay

Use cases:
- Bug fixes
- Recomputations

---

## 5. Immutable Log Pattern

Kafka acts as:
- Source of truth

Events:
- Never modified
- Only appended

---

## 6. Materialized View Pattern

- Precomputed results

Lambda:
- Batch + stream views

Kappa:
- Stream-built views

---

## 🔄 Real Example (E-Commerce)

### Lambda
- Batch → Daily reports
- Stream → Live orders

### Kappa
- Orders → Kafka
- Kafka → Flink
- Flink → Aggregated views

Replay Kafka for recompute

---

# 🚀 When to Use

## Use Lambda when:
- Heavy analytics
- Compliance requirements
- Historical recomputation needed

## Use Kappa when:
- Real-time systems
- Simpler architecture preferred
- Kafka-based pipelines

---

# 🧠 Final Mental Model

Lambda:
> “Process twice for correctness”

Kappa:
> “Process once, replay when needed”

---

# 🧩 Conclusion

Lambda is powerful but complex.  
Kappa is simpler and modern, enabled by strong streaming systems.

Modern systems often prefer:
- Kafka + Flink → Kappa-style architecture
