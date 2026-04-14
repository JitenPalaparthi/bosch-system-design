# 📘 Non-Functional Requirements (NFR) Scorecards – Complete Guide

---

# 🧭 What are NFRs?

<details open>
<summary><strong>📖 Explanation</strong></summary>

Non-Functional Requirements (NFRs) define **how a system behaves**, rather than what it does.

They cover system qualities like:
- Performance
- Scalability
- Reliability
- Security
- Availability
- Maintainability

---

### Key Idea
> Functional = WHAT system does  
> NFR = HOW WELL system does it

</details>

---

# 🧾 What is an NFR Scorecard?

<details open>
<summary><strong>📖 Explanation</strong></summary>

An NFR Scorecard is a **structured evaluation framework** used to:

- Measure system quality attributes
- Compare design options
- Track system readiness

---

### Why Scorecards?
- Quantifies architecture decisions
- Helps in trade-off analysis
- Enables objective comparisons

</details>

---

# 🧩 NFR Categories

<details open>
<summary><strong>Click to expand</strong></summary>

| Category | Description | Example Metric |
|----------|------------|---------------|
| Performance | Speed of system | Latency < 200ms |
| Scalability | Handle growth | 1M users |
| Availability | Uptime | 99.99% |
| Reliability | Failure tolerance | MTBF |
| Security | Protection | OWASP compliance |
| Maintainability | Ease of updates | Deployment time |
| Observability | Monitoring | Logs, metrics |

</details>

---

# 📊 NFR Scorecard Template

<details open>
<summary><strong>Click to expand</strong></summary>

| NFR | Target | Current | Score (1-5) | Notes |
|-----|--------|--------|-------------|------|
| Performance | <200ms | 250ms | 3 | Needs optimization |
| Availability | 99.99% | 99.9% | 4 | Acceptable |
| Scalability | 1M users | 500K | 3 | Needs scaling |
| Security | High | Medium | 3 | Improve auth |
| Reliability | High | High | 5 | Good |

---

### Score Meaning

| Score | Meaning |
|------|--------|
| 1 | Poor |
| 2 | Below expectations |
| 3 | Acceptable |
| 4 | Good |
| 5 | Excellent |

</details>

---

# 🧠 How to Use NFR Scorecards

<details open>
<summary><strong>Click to expand</strong></summary>

### Step 1: Define Requirements
- Identify key NFRs for system

### Step 2: Assign Targets
- Example: Latency < 200ms

### Step 3: Measure Current State
- Collect metrics

### Step 4: Score Each NFR
- Based on gap

### Step 5: Analyze Trade-offs
- Example: Performance vs Cost

</details>

---

# ⚖️ Example: Monolith vs Microservices

<details open>
<summary><strong>Click to expand</strong></summary>

| NFR | Monolith | Microservices |
|-----|----------|--------------|
| Performance | 4 | 3 |
| Scalability | 2 | 5 |
| Availability | 3 | 5 |
| Complexity | 2 | 5 |
| Deployment | 2 | 4 |

---

### Insight

- Monolith → Simpler, less scalable  
- Microservices → Complex but scalable  

</details>

---

# 🎬 Real Use Case: Netflix

<details open>
<summary><strong>Click to expand</strong></summary>

### Requirements
- High availability (99.99%)
- Global scalability
- Low latency streaming

---

### Scorecard Decision

| NFR | Score | Decision |
|-----|------|---------|
| Availability | 5 | Multi-region |
| Scalability | 5 | Microservices |
| Performance | 4 | CDN usage |

---

### Result
- Adopt microservices + CDN + caching

</details>

---

# 🔄 Trade-off Thinking

<details open>
<summary><strong>Click to expand</strong></summary>

### Common Conflicts

- Performance vs Cost
- Consistency vs Availability (CAP)
- Scalability vs Simplicity

---

### Key Principle

> No system can maximize all NFRs simultaneously

</details>

---

# 📌 Final Insight

> NFR Scorecards turn architecture from opinion into **measurable engineering decisions**

