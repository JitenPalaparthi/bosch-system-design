# 🚀 API Demo – Usage Guide

This is a sample Flask API demonstrating API design principles like versioning, validation, pagination, and consistent responses.

---

## 🔧 Setup

```bash
pip install -r requirements.txt
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

## 📌 Base URL

```
http://127.0.0.1:5000/api/v1
```

---

## 🧪 Endpoints

### 1. Health Check

```bash
curl http://127.0.0.1:5000/health
```

---

### 2. Create User

```bash
curl -X POST http://127.0.0.1:5000/api/v1/users \
-H "Content-Type: application/json" \
-d '{
  "name": "John",
  "email": "john@example.com"
}'
```

---

### 3. Get All Users

```bash
curl "http://127.0.0.1:5000/api/v1/users?page=1&limit=10&search=john"
```

---

### 4. Get User by ID

```bash
curl http://127.0.0.1:5000/api/v1/users/1
```

---

### 5. Update User

```bash
curl -X PUT http://127.0.0.1:5000/api/v1/users/1 \
-H "Content-Type: application/json" \
-d '{
  "name": "John Updated",
  "email": "john.updated@example.com"
}'
```

---

### 6. Delete User

```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/users/1
```

---

## ❗ Error Example

```bash
curl http://127.0.0.1:5000/api/v1/users/999
```

---

## 📊 Query Parameters

- page: Page number  
- limit: Number of records  
- search: Filter users by name  

---

## ✅ Summary

- RESTful design  
- Versioning (/v1)  
- Pagination & filtering  
- Validation & error handling  
