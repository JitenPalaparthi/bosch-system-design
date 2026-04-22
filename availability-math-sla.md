# Availability Math & SLAs (System Design)

## 🧠 Overview

Availability is a key **Non-Functional Requirement (NFR)** in system design.  
It defines how often a system is operational and accessible.

---

# 📊 What is Availability?

Availability = Uptime / (Uptime + Downtime)

Example:
If a system is up for 99 hours out of 100 hours:

Availability = 99 / (99 + 1) = 99%

---

# 🧮 Availability Formula

Availability = MTBF / (MTBF + MTTR)

Where:
- MTBF = Mean Time Between Failures
- MTTR = Mean Time To Repair

---

# 📉 SLA (Service Level Agreement)

SLA is a **contract** that defines:
- Expected availability
- Performance guarantees
- Penalties if not met

---

# 🎯 SLA vs SLO vs SLI

| Term | Meaning |
|------|--------|
| SLA | Contract with customer |
| SLO | Internal target |
| SLI | Measurement metric |

---

# 📊 Availability Levels (Nines)

| Availability | Downtime per Year |
|--------------|------------------|
| 99%          | ~3.65 days       |
| 99.9%        | ~8.76 hours      |
| 99.99%       | ~52 minutes      |
| 99.999%      | ~5 minutes       |

---

# 🔧 How to Improve Availability

- Redundancy (multi-node, multi-region)
- Load balancing
- Failover mechanisms
- Health checks
- Circuit breakers

---

# 🧠 Real Example

E-commerce website:

- SLA: 99.9%
- Downtime allowed ≈ 8.76 hours/year

To achieve:
- Use multiple servers
- Deploy across regions
- Use caching and CDN

---

# ⚖️ Trade-offs

Higher availability:
- Increases cost
- Increases complexity

---

# 🧩 Conclusion

Availability is a balance between:
- Cost
- Complexity
- Business requirements

SLA ensures accountability and reliability.
