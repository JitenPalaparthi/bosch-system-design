# Architecture Defense (Panel Style)

## 1. Overview

A Panel-Style Architecture Defense simulates a real-world review board where multiple experts challenge your system design from different angles.

Typical panel roles:
- Architect (scalability & design)
- SRE (reliability & failure handling)
- Security Engineer
- Product/Business Stakeholder

Goal:
Stress-test your architecture across multiple dimensions simultaneously.

---

## 2. Panel Roles & Focus Areas

### 2.1 Chief Architect
Focus:
- System design correctness
- Trade-offs
- Technology choices

Questions:
- Why microservices?
- Why this database?
- What are your bottlenecks?

---

### 2.2 SRE (Site Reliability Engineer)
Focus:
- Availability
- Failure handling
- Observability

Questions:
- What happens if a service crashes?
- How do you ensure 99.99% uptime?
- What is your retry/backoff strategy?

---

### 2.3 Security Engineer
Focus:
- Authentication & Authorization
- Data protection
- Threat modeling

Questions:
- How do you prevent data breaches?
- How is data encrypted?
- How do you handle API abuse?

---

### 2.4 Product Manager
Focus:
- User experience
- Cost vs value
- Feature impact

Questions:
- Why is latency acceptable?
- What is the cost impact?
- How fast can we launch?

---

## 3. Structure of Panel Defense

### Step 1: Design Pitch (10–15 mins)
- System overview
- Key components
- Data flow

---

### Step 2: Deep Dive (15–20 mins)
- Scaling strategy
- Data storage
- Caching
- Async pipelines

---

### Step 3: Panel Cross-Examination (20–30 mins)
Panel members ask rapid-fire questions.

---

### Step 4: Trade-off Justification
You must justify:
- Why not simpler?
- Why not cheaper?
- Why not more scalable?

---

## 4. Sample Panel Drill

### System:
Design a video streaming platform (Netflix-like)

---

### Architect Questions
- Why use CDN?
- Why object storage instead of block storage?
- How do you scale read traffic?

---

### SRE Questions
- What if a region goes down?
- How do you handle failover?
- What is your recovery time objective (RTO)?

---

### Security Questions
- How do you protect video content?
- How do you handle authentication?
- How do you prevent DDoS?

---

### Product Questions
- What is acceptable buffering time?
- How much will this cost per user?
- Can we reduce infrastructure cost?

---

## 5. Evaluation Criteria

### 5.1 Technical Depth
- Clear understanding of components
- Strong reasoning

---

### 5.2 Trade-off Awareness
- Latency vs cost
- Consistency vs availability

---

### 5.3 Failure Thinking
- Identifies weak points
- Has fallback strategies

---

### 5.4 Communication
- Clear explanations
- Structured thinking

---

## 6. Common Pitfalls

- Ignoring one panel perspective (e.g., security)
- Over-engineering
- No cost consideration
- Weak failure handling

---

## 7. Practice Template

Use this template:

### System:
____________________

### Constraints:
____________________

### Design:
____________________

### Architect Defense:
____________________

### SRE Defense:
____________________

### Security Defense:
____________________

### Product Defense:
____________________

---

## 8. Advanced Tips

- Always quantify:
  - Latency (p99)
  - Availability (% uptime)
- Think in failure scenarios first
- Justify every technology choice
- Keep design simple but scalable

---

## 9. Conclusion

Panel-style architecture defense is the closest simulation to real-world architecture reviews and senior-level interviews.

It builds:
- Multi-dimensional thinking
- Trade-off reasoning
- Production readiness mindset
