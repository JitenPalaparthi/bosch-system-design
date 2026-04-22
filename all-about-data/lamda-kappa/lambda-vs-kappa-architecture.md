# Lambda vs Kappa Architecture (System Design)

## 🧠 Overview

Both Lambda and Kappa are architectures for processing large-scale data systems.

- **Lambda**: Batch + Stream processing
- **Kappa**: Stream-only processing

---

# 🏗️ Lambda Architecture

## Core Idea
Combine batch processing (accuracy) with real-time processing (low latency).

## Layers

### 1. Batch Layer
- Stores full data
- Recomputes results

### 2. Speed Layer
- Processes real-time data

### 3. Serving Layer
- Combines both outputs

## Flow

```
Data → Batch Layer → Batch Views
     → Speed Layer → Real-time Views
     → Serving Layer → Query
```

## Pros
- High accuracy
- Fault tolerant

## Cons
- Complex
- Duplicate logic

---

# ⚡ Kappa Architecture

## Core Idea
Use only streaming for all processing.

## Components

### 1. Stream Processing
- Handles both real-time and historical via replay

### 2. Log Storage (Kafka)
- Stores events

### 3. Serving Layer
- Query processed data

## Flow

```
Data → Kafka → Stream Processing → Serving DB → Query
```

## Pros
- Simpler
- Easier maintenance

## Cons
- Replay cost
- Needs strong streaming infra

---

# ⚖️ Comparison

| Feature | Lambda | Kappa |
|--------|--------|-------|
| Processing | Batch + Stream | Stream only |
| Complexity | High | Low |
| Latency | Medium | Low |
| Maintenance | Hard | Easy |

---

# 🧠 When to Use

## Lambda
- Heavy analytics
- Historical recomputation

## Kappa
- Real-time systems
- Event-driven apps

---

# 🧩 Conclusion

Lambda = Accuracy + Complexity  
Kappa = Simplicity + Streaming
