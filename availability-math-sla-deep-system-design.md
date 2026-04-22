
# Availability Math & SLAs 

## 1) Why Availability Matters

Availability is one of the most important **non-functional requirements (NFRs)** in system design.  
It answers a simple business question:

> **For what percentage of time is the system usable to customers?**

This affects:
- Revenue
- User trust
- Contractual commitments
- Operational design
- Cost of redundancy

A highly available system is not just “running”; it must be **able to serve correct requests within acceptable conditions**.

---

## 2) Core Definitions

## Availability
Availability is the fraction of time a system is operational and able to serve traffic.

**Formula:**

```text
Availability = Uptime / (Uptime + Downtime)
```

If a system is available for 999 hours and unavailable for 1 hour:

```text
Availability = 999 / 1000 = 99.9%
```

---

## Reliability vs Availability

These terms are related but different:

- **Reliability** = how long a system runs before failing
- **Availability** = how often the system is usable overall

A system may fail often but recover very quickly, leading to acceptable availability.
A system may fail rarely but take a very long time to recover, causing poor availability.

---

## MTBF and MTTR

A common engineering view is:

```text
Availability = MTBF / (MTBF + MTTR)
```

Where:
- **MTBF** = Mean Time Between Failures
- **MTTR** = Mean Time To Repair / Recover

### Example
If:
- MTBF = 999 hours
- MTTR = 1 hour

Then:

```text
Availability = 999 / (999 + 1) = 99.9%
```

### Interpretation
- Increase MTBF → fewer failures
- Decrease MTTR → faster recovery
- Both improve availability

---

## 3) SLA, SLO, and SLI

These are often confused, so keep them clearly separated.

## SLI — Service Level Indicator
An **SLI** is the actual measured metric.

Examples:
- Successful request ratio
- API latency under 300 ms
- Percentage of healthy checks passing
- Order placement success rate

### Example SLI
```text
Availability SLI = successful requests / total valid requests
```

---

## SLO — Service Level Objective
An **SLO** is the target you want engineering to hit.

Examples:
- 99.95% monthly API availability
- 95% of requests under 200 ms
- Error rate below 0.1%

SLO is an internal engineering target.

---

## SLA — Service Level Agreement
An **SLA** is the formal commitment to customers, usually contractual.

It may include:
- Guaranteed uptime
- Support response time
- Credits or penalties if missed
- Definition of what counts as downtime
- Exclusions (maintenance, force majeure, customer misconfiguration)

### Practical relationship
- **SLI** = what you measure
- **SLO** = what you aim for internally
- **SLA** = what you legally/commercially promise externally

A common practice is:

```text
SLO > SLA
```

Example:
- Internal SLO = 99.95%
- External SLA = 99.9%

That buffer protects the business.

---

## 4) The “Nines” and Allowed Downtime

Availability targets are commonly expressed in “nines”.

| Availability | Downtime / Year | Downtime / Month | Downtime / Week |
|---|---:|---:|---:|
| 99% | 3.65 days | 7.31 hours | 1.68 hours |
| 99.5% | 1.83 days | 3.65 hours | 50.4 minutes |
| 99.9% | 8.76 hours | 43.8 minutes | 10.08 minutes |
| 99.95% | 4.38 hours | 21.9 minutes | 5.04 minutes |
| 99.99% | 52.56 minutes | 4.38 minutes | 1.01 minutes |
| 99.999% | 5.26 minutes | 26.3 seconds | 6.05 seconds |

### Important note
The higher the availability target, the more expensive and operationally demanding the system becomes.

Moving from:
- 99.9% to 99.99% is not “small”
- it is a major architecture and operations jump

---

## 5) How Availability is Actually Measured

Availability is not just “server is up”.

You must define:
- What user journey matters?
- What counts as success?
- What counts as downtime?
- What is the measurement window?

### Examples of different availability definitions

#### Infrastructure availability
- Load balancer is reachable
- VM is running
- Pod is healthy

This can be misleading because the app may still be unusable.

#### Application availability
- API returns successful responses
- Login works
- Checkout works

Better than infrastructure-only measurement.

#### User-experience availability
- A core user transaction completes successfully within latency SLO

This is often the most meaningful.

### Better definition example
For an e-commerce system:

```text
Availability = successful checkout requests within 2 seconds / all valid checkout requests
```

This is better than saying “the server responded with 200 OK”.

---

## 6) Error Budgets

An **error budget** is how much unreliability you are allowed before breaching the SLO.

### Example
If monthly SLO is 99.9%, then allowed failure is:

```text
100% - 99.9% = 0.1%
```

That 0.1% is your error budget.

### Why it matters
Error budgets help balance:
- shipping features
- platform stability
- risk-taking in releases

If the team is burning too much error budget:
- freeze risky releases
- focus on reliability work
- improve rollback, alerting, testing, failover

---

## 7) Availability in Series and Parallel Systems

This is critical in system design interviews and architecture design.

## Series Availability
If a request depends on **all components** working, overall availability decreases.

**Formula:**

```text
A_total = A1 × A2 × A3 × ...
```

### Example
Suppose request path requires:
- API Gateway = 99.95%
- Auth Service = 99.9%
- Orders Service = 99.9%
- Payments Service = 99.95%

Then:

```text
A_total = 0.9995 × 0.999 × 0.999 × 0.9995
        ≈ 0.9970
        = 99.70%
```

### Insight
Even when each component looks excellent individually, the end-to-end path can be much worse.

This is why critical flows should avoid too many synchronous dependencies.

---

## Parallel / Redundant Availability
If either of two replicas can serve traffic, availability improves.

For two independent components:

```text
A_parallel = 1 - (1 - A1)(1 - A2)
```

### Example
Two identical instances, each with 99.9% availability:

```text
A_parallel = 1 - (0.001 × 0.001)
           = 1 - 0.000001
           = 0.999999
           = 99.9999%
```

### Important caveat
This assumes:
- failures are independent
- traffic can be rerouted correctly
- failover is quick
- no common-mode failures exist

In practice, common dependencies reduce the real gain.

---

## 8) Common-Mode Failures

Redundancy is useful only if failures are not shared.

Two app replicas are **not** truly independent if they share:
- same database
- same AZ
- same load balancer
- same config system
- same DNS dependency
- same deployment bug
- same cloud account limits

### Examples of common-mode failure
- Bad config pushed to all replicas
- Shared database outage
- Same region failure
- Shared cache cluster failure
- Expired certificate
- DNS outage

This is why multi-instance design alone does not guarantee high availability.

---

## 9) Availability Patterns in System Design

## Active-Passive
One node handles traffic, secondary waits for failover.

### Pros
- Simple
- Easier consistency
- Easier failover reasoning

### Cons
- Some capacity wasted
- Failover time may hurt SLA
- Passive may be stale if replication lags

### Use cases
- Primary database with standby
- Disaster recovery region

---

## Active-Active
Multiple nodes/regions serve traffic simultaneously.

### Pros
- Better utilization
- Better regional resilience
- Lower latency for distributed users

### Cons
- Harder consistency
- Harder conflict resolution
- More complex routing and observability

### Use cases
- Read-heavy global applications
- Multi-region API frontends
- CDN-backed content services

---

## N+1 Redundancy
You need N units to handle peak load, but deploy N+1 or more.

Example:
- Need 4 servers to survive peak
- Deploy 5 or 6

This allows one unit to fail without service loss.

---

## Graceful Degradation
Instead of full outage, disable non-critical features.

Example:
- Product recommendations fail → checkout still works
- Search ranking degrades → basic search still works
- Profile image service fails → default avatar shown

This protects business-critical paths and improves real-world availability.

---

## 10) Availability vs Latency vs Consistency

Higher availability often conflicts with other goals.

### Examples
- Strong consistency across regions may reduce availability during partitions
- Heavy synchronous validations increase failure surface
- Complex request chains increase latency and failure propagation

### CAP relation
Under network partition:
- if you choose consistency, availability may drop
- if you choose availability, data may be temporarily stale

### PACELC relation
Even without partitions:
- stronger consistency often adds latency

So availability design is never isolated; it interacts with:
- consistency
- latency
- throughput
- cost

---

## 11) SLA Design Considerations

A useful SLA must clearly define:

### Scope
Which service is covered?
- Public API?
- Admin API?
- Entire platform?
- Specific premium feature?

### Measurement window
- Monthly is very common
- Sometimes weekly or quarterly

### Measurement source
- Provider monitoring?
- Third-party synthetic probes?
- Client-side telemetry?

### What counts as downtime?
Need explicit rules such as:
- HTTP 5xx responses?
- timeouts?
- latency above threshold?
- maintenance excluded or included?

### Exclusions
Typical exclusions:
- Scheduled maintenance
- Customer misuse
- Force majeure
- Third-party dependency outages outside scope
- Beta features

### Service credits
If SLA is violated:
- customer receives credits
- refund percentage depends on severity

---

## 12) Sample SLA Structure

```text
Service: Public Checkout API
Measurement Window: Monthly
SLA: 99.9% monthly uptime
Downtime Definition:
  Any 5-minute interval in which more than 5% of valid requests fail
  or exceed 2 seconds latency

Exclusions:
  - Scheduled maintenance announced 72 hours in advance
  - Upstream payment processor outage outside our boundary
  - Customer-side network failures

Service Credits:
  - <99.9% and >=99.0% → 10% credit
  - <99.0% and >=95.0% → 25% credit
  - <95.0% → 50% credit
```

This is much better than a vague statement like “we guarantee high availability”.

---

## 13) Example: Single-Region E-Commerce Checkout

Suppose the checkout path is:

```text
Client
  -> CDN
  -> Load Balancer
  -> API Gateway
  -> Auth Service
  -> Cart Service
  -> Order Service
  -> Payment Gateway
  -> Database
```

Assume these simplified availabilities:

| Component | Availability |
|---|---:|
| CDN | 99.95% |
| Load Balancer | 99.99% |
| API Gateway | 99.95% |
| Auth Service | 99.9% |
| Cart Service | 99.9% |
| Order Service | 99.95% |
| Payment Gateway | 99.9% |
| Database | 99.95% |

Approximate end-to-end availability:

```text
0.9995 × 0.9999 × 0.9995 × 0.999 × 0.999 × 0.9995 × 0.999 × 0.9995
≈ 0.9958
≈ 99.58%
```

### Insight
Even though every component looks “four nines-ish” or close, the full synchronous chain falls below 99.9%.

### Design improvements
- Reduce synchronous hops
- Cache identity/session state safely
- Make non-critical steps async
- Introduce fallback payment methods
- Use circuit breakers
- Add DB failover/read replicas where suitable
- Separate checkout-critical systems from optional systems

---

## 14) Example: Availability Improvement with Redundancy

Suppose your Orders API instance availability is 99.5%.

With two independent instances behind a load balancer:

```text
A_parallel = 1 - (1 - 0.995)^2
           = 1 - (0.005)^2
           = 1 - 0.000025
           = 0.999975
           = 99.9975%
```

That is a huge gain on paper.

### But in reality
If both instances depend on:
- same DB
- same region
- same config
- same deployment pipeline

your true availability may still be much lower.

---

## 15) Multi-AZ and Multi-Region Availability

## Multi-AZ
Deploy across availability zones inside one region.

### Benefits
- Survive rack/AZ failures
- Better resilience against localized outages

### Limitations
- Region-wide outages still hurt
- Shared control plane dependencies may still exist

---

## Multi-Region
Deploy across separate regions.

### Benefits
- Survive full region outage
- Better disaster resilience
- Better latency for geo-distributed users

### Challenges
- Data replication complexity
- Strong consistency costs
- Failover orchestration
- DNS/routing complexity
- Operational complexity

### Typical patterns
- Active-passive DR
- Active-active reads
- Active-active stateless frontends
- Per-region write ownership

---

## 16) Availability and Databases

The database is often the real limiter.

### Why
App tiers are easy to replicate.
Stateful systems are harder.

### Common database strategies
- Primary + replica
- Multi-AZ managed database
- Read replicas
- Sharding
- Consensus systems for metadata/control planes
- Multi-region replication

### Key trade-offs
- Higher write consistency can lower availability during network issues
- Automatic failover improves MTTR
- Asynchronous replication improves availability but may risk data loss
- Synchronous replication improves consistency but increases latency/failure sensitivity

---

## 17) Design Techniques to Improve Availability

## 1. Remove single points of failure
Examples:
- single DB
- single cache
- single message broker
- single load balancer
- single DNS provider

---

## 2. Reduce synchronous dependencies
If checkout waits on:
- recommendations
- analytics
- email
- audit export

then availability drops unnecessarily.

Move non-critical steps to async queues.

---

## 3. Use circuit breakers
When a dependency is unhealthy:
- fail fast
- degrade gracefully
- avoid cascading failure

---

## 4. Timeouts and retries
Useful, but dangerous if misconfigured.

### Bad retry behavior can:
- amplify load
- create retry storms
- worsen outages

Use:
- capped retries
- exponential backoff
- jitter
- idempotency

---

## 5. Bulkheads
Isolate resources so one failure domain does not consume everything.

Examples:
- separate worker pools
- separate queues
- separate connection pools

---

## 6. Health checks and failover automation
Fast detection + fast failover reduces MTTR.

---

## 7. Safe deployments
Use:
- canary
- blue-green
- rolling deployment with readiness gates
- feature flags
- instant rollback

Deployment incidents are a major availability risk.

---

## 8. Observability
Need:
- metrics
- logs
- traces
- synthetic probes
- alerting
- user journey monitoring

If you cannot detect outages quickly, MTTR increases.

---

## 18) Availability Anti-Patterns

Avoid these:

- Too many synchronous calls in a request path
- Treating uptime of servers as business availability
- Ignoring dependency availability
- No clear downtime definition
- Chasing five nines without business need
- Shared hidden dependencies
- Single-region design with global SLA promises
- No failover drills
- No chaos testing
- No rollback strategy

---

## 19) Business-Driven Availability Targets

Not every system needs the same target.

### Typical examples

#### Internal reporting portal
- 99% may be acceptable

#### B2B dashboard
- 99.5% or 99.9%

#### Consumer e-commerce checkout
- 99.9% or 99.95%

#### Payments or core banking path
- very high target, but with extreme cost and rigor

### Rule
Choose availability target based on:
- revenue impact
- user expectations
- operational cost
- compliance needs
- engineering maturity

Do not choose “five nines” just because it sounds good.

---

## 20) Interview-Style Example Answer

### Question
How would you design a system for 99.95% availability?

### Strong answer structure
1. Define what availability means for the business path
2. Identify critical request path
3. Calculate current chain availability
4. Remove single points of failure
5. Add redundancy where it truly helps
6. Reduce synchronous dependencies
7. Improve MTTR through automation
8. Add observability and error budgets
9. Design realistic SLA/SLO/SLI
10. Validate with failure testing

---

## 21) Quick Formula Summary

### Basic availability
```text
Availability = Uptime / (Uptime + Downtime)
```

### MTBF / MTTR view
```text
Availability = MTBF / (MTBF + MTTR)
```

### Series components
```text
A_total = A1 × A2 × A3 × ...
```

### Parallel redundancy
```text
A_parallel = 1 - (1 - A1)(1 - A2)
```

### Error budget
```text
Error Budget = 100% - SLO
```

---

## 22) Final Mental Model

Think of availability in three layers:

### 1. Math
- uptime %
- downtime budget
- series vs parallel calculation

### 2. Architecture
- redundancy
- failover
- dependency design
- graceful degradation

### 3. Operations
- detection
- rollback
- incident response
- deployment safety
- observability

Real availability comes from all three together.

---

## 23) Final Conclusion

Availability is not just a percentage in a slide deck.  
It is the outcome of:

- good architecture
- clear measurement
- strong operations
- fast recovery
- disciplined dependency management

**SLA** is the business promise.  
**SLO** is the engineering target.  
**SLI** is the measured reality.

And the most important system design lesson is this:

> End-to-end availability is usually lower than people expect, because dependencies multiply failure probability.

So when designing reliable systems:
- minimize synchronous dependencies
- add meaningful redundancy
- reduce MTTR aggressively
- measure what users actually experience
- set targets that match business value
