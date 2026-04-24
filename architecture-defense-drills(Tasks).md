# Architecture Defense Drills (System Design Practice)

## 1. Introduction

These drills simulate real-world architecture defense scenarios where you must justify design decisions under pressure.

Each drill includes:
- Problem Statement
- Constraints
- Key Questions (Defense Round)

---

## 2. Drill 1: URL Shortener (TinyURL)

### Problem
Design a URL shortening service like TinyURL.

### Constraints
- 10M requests/day
- Low latency redirects
- High read-to-write ratio (100:1)

### Defense Questions
- Why use NoSQL over SQL?
- How do you handle hash collisions?
- What is your caching strategy?
- What happens if cache fails?

---

## 3. Drill 2: E-commerce Platform

### Problem
Design an Amazon-like system.

### Constraints
- Millions of users
- High traffic during sales
- Inventory consistency is critical

### Defense Questions
- How do you prevent overselling?
- Why use eventual consistency or strong consistency?
- How do you handle flash sale spikes?
- What is your database sharding strategy?

---

## 4. Drill 3: Video Streaming System

### Problem
Design a Netflix/YouTube-like system.

### Constraints
- 1M concurrent users
- Global audience
- Heavy bandwidth usage

### Defense Questions
- Why use CDN?
- How do you reduce buffering?
- What happens if edge server fails?
- How do you store large video files?

---

## 5. Drill 4: Real-time Chat System

### Problem
Design WhatsApp-like chat.

### Constraints
- Real-time delivery
- Billions of messages/day
- Low latency

### Defense Questions
- Why WebSockets over HTTP?
- How do you ensure message ordering?
- What happens if user reconnects?
- How do you store chat history?

---

## 6. Drill 5: Ride Sharing System

### Problem
Design Uber-like system.

### Constraints
- Real-time location tracking
- Matching drivers and riders
- High availability

### Defense Questions
- How do you match drivers efficiently?
- What happens if GPS data is delayed?
- How do you handle surge pricing?
- How do you scale location updates?

---

## 7. Drill 6: Log Aggregation System

### Problem
Design a system like ELK stack.

### Constraints
- High ingestion rate
- Near real-time search
- Distributed system

### Defense Questions
- Why use Kafka?
- How do you handle backpressure?
- What happens if consumer lags?
- How do you index logs?

---

## 8. Drill 7: Payment System

### Problem
Design a payment gateway.

### Constraints
- Strong consistency
- High security
- No data loss

### Defense Questions
- How do you ensure idempotency?
- What happens on double payment?
- How do you handle failures?
- Why use transactions?

---

## 9. Drill 8: Notification System

### Problem
Design a notification service (email, SMS, push).

### Constraints
- High fan-out
- Retry mechanisms
- Multi-channel delivery

### Defense Questions
- How do you handle retries?
- What if SMS provider fails?
- How do you prioritize notifications?
- How do you scale fan-out?

---

## 10. Drill 9: Search Engine

### Problem
Design a search system.

### Constraints
- Fast query response
- Large dataset
- Ranking relevance

### Defense Questions
- Why use inverted index?
- How do you rank results?
- What happens if index is stale?
- How do you scale search queries?

---

## 11. Drill 10: Distributed Cache

### Problem
Design Redis-like cache system.

### Constraints
- In-memory storage
- High throughput
- Low latency

### Defense Questions
- How do you handle eviction?
- What happens on node failure?
- How do you partition data?
- How do you maintain consistency?

---

## 12. How to Use These Drills

1. Pick one drill
2. Design the system
3. Answer all defense questions
4. Add failure scenarios
5. Justify trade-offs

---

## 13. Pro Tip

Always think in this flow:

Constraints → Design → Trade-offs → Failure → Recovery

---

## 14. Conclusion

Practicing these drills will help you:
- Improve system design thinking
- Prepare for architecture interviews
- Build production-ready mindset
