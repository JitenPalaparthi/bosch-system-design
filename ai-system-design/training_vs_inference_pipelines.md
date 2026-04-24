# 📘 Training vs Inference Pipelines (System Design Perspective)

---

## 🧠 Overview

In Machine Learning systems, pipelines are broadly divided into:

- **Training Pipeline** → Builds the model  
- **Inference Pipeline** → Uses the model for predictions  

---

# 🔷 Training Pipeline

## 🎯 Goal
To learn patterns from data and produce a trained model artifact.

## 🏗️ Flow

Raw Data → Ingestion → Cleaning → Feature Engineering → Train → Evaluate → Model Registry → Deploy

## ⚙️ Key Points

- Batch processing
- High latency (minutes to hours)
- Large datasets (GB–PB)
- Uses tools like Spark, Airflow, MLflow

---

# 🔶 Inference Pipeline

## 🎯 Goal
To serve predictions in real-time.

## 🏗️ Flow

Client → API → Feature Store → Model → Prediction → Response

## ⚙️ Key Points

- Real-time processing
- Low latency (ms)
- High availability
- Uses FastAPI, TensorFlow Serving, Kubernetes

---

# 🔁 Comparison

| Feature | Training | Inference |
|--------|--------|---------|
| Purpose | Build model | Use model |
| Latency | High | Low |
| Data | Large | Small |
| Execution | Batch | Real-time |

---

# 🔄 Integration

Training → Model Registry → Deployment → Inference

---

# 🧠 Advanced Concepts

- Feature Drift
- Model Drift
- Continuous Training
- A/B Testing

---

# 🏗️ Production Architecture

Data Lake → Training → Model Registry → Deployment → Inference APIs

---

# 📌 Key Takeaways

- Training = Learning phase  
- Inference = Execution phase  
- Training is compute-heavy  
- Inference is latency-sensitive  
