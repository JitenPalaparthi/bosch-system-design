# AI Failure Models (Production Perspective)

## 1. Overview
AI systems fail in predictable patterns. Understanding them is critical for reliability and production readiness.

## 2. Taxonomy of AI Failures

### Data Failures
- Data Drift
- Concept Drift
- Data Quality Issues
- Sampling Bias

### Model Failures
- Overfitting
- Underfitting
- Model Staleness
- Adversarial Attacks

### System Failures
- Latency Issues
- Throughput Bottlenecks
- Dependency Failures
- Resource Exhaustion

### LLM Failures
- Hallucinations
- Prompt Sensitivity
- Context Limits
- Token Explosion

### Governance Failures
- Bias
- Privacy Leakage
- Lack of Explainability

## 3. Detection
- Drift Monitoring
- Accuracy Drop
- Latency Metrics (p95, p99)

## 4. Mitigation
- Retraining Pipelines
- A/B Testing
- Circuit Breakers
- RAG + Guardrails

## 5. Key Takeaway
AI failures must be handled with:
- Monitoring
- Fallbacks
- Continuous improvement
