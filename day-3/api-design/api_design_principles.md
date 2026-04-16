# API Design Principles

A practical guide to designing APIs that are easy to use, maintain, secure, and evolve.

---

## 1. Why API design matters

A well-designed API helps consumers:

- understand endpoints quickly
- integrate with fewer bugs
- recover from errors predictably
- scale usage without surprises

A poorly designed API usually creates confusion around naming, status codes, payload structure, versioning, and behavior.

---

## 2. Core principles

### 2.1 Consistency
Use the same naming, patterns, and response shapes across the API.

**Good**

```http
GET /v1/users
GET /v1/users/123
GET /v1/orders
GET /v1/orders/101
```

**Avoid**

```http
GET /getUsers
POST /fetchOrderById
GET /user_list
```

---

### 2.2 Simplicity
An API should be easy to understand on first use.

**Good**

```http
GET /v1/products/10
```

**Too complex**

```http
POST /v1/productService?action=read&id=10
```

---

### 2.3 Resource-oriented design
In REST-style APIs, URLs should represent resources.

| Operation | Endpoint |
|---|---|
| List users | `GET /v1/users` |
| Get one user | `GET /v1/users/{id}` |
| Create user | `POST /v1/users` |
| Full update | `PUT /v1/users/{id}` |
| Partial update | `PATCH /v1/users/{id}` |
| Delete user | `DELETE /v1/users/{id}` |

Prefer nouns like `users`, `orders`, and `payments` over verbs like `createUser`.

---

### 2.4 Correct HTTP methods
Use verbs according to standard semantics.

- `GET` → read
- `POST` → create
- `PUT` → replace
- `PATCH` → partial update
- `DELETE` → remove

---

### 2.5 Meaningful status codes
Status codes should accurately describe the result.

| Code | Meaning |
|---|---|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created |
| `204 No Content` | Successful request with no response body |
| `400 Bad Request` | Invalid input |
| `401 Unauthorized` | Authentication missing/invalid |
| `403 Forbidden` | Authenticated but not allowed |
| `404 Not Found` | Resource missing |
| `409 Conflict` | State conflict / duplicate |
| `422 Unprocessable Entity` | Validation failed |
| `500 Internal Server Error` | Server failure |

---

### 2.6 Clear error responses
Errors should help the client fix the problem.

**Bad**

```json
{"error": "failed"}
```

**Better**

```json
{
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email format is invalid",
    "details": {
      "field": "email"
    }
  }
}
```

---

### 2.7 Statelessness
Each request should contain what the server needs to process it.

Examples:

- include auth token in each request
- include all required path/query/body data
- do not depend on hidden session state unless your architecture explicitly requires it

---

### 2.8 Versioning
APIs evolve. Version them so older clients do not break.

**Common pattern**

```http
/v1/users
/v2/users
```

---

### 2.9 Idempotency
Some operations should be safe to repeat.

Examples:

- `PUT /v1/users/10` with same payload repeatedly should produce same final state
- `DELETE /v1/users/10` repeated should still leave the resource deleted

This is especially important for retries.

---

### 2.10 Pagination, filtering, sorting
Do not return everything at once.

Examples:

```http
GET /v1/users?page=1&limit=20
GET /v1/products?category=books
GET /v1/orders?sort=-createdAt
GET /v1/users?search=john
```

---

### 2.11 Validation
Reject bad data early and explicitly.

Examples:

- missing required fields
- invalid email
- negative amount
- unsupported enum value

---

### 2.12 Security by design
Security should not be added later as an afterthought.

Include:

- HTTPS
- authentication
- authorization
- input validation
- rate limiting
- audit logging where required

---

### 2.13 Backward compatibility
Try to make changes without breaking consumers.

Safer changes:

- adding optional fields
- adding new endpoints
- adding new query parameters with sensible defaults

Risky changes:

- removing fields
- changing meaning of existing fields
- changing status code behavior unexpectedly

---

### 2.14 Observability
APIs should be easy to debug and operate.

Useful capabilities:

- request IDs
- structured logging
- metrics
- tracing
- health endpoints

---

### 2.15 Documentation
A good API should be self-explanatory and documented.

Documentation should include:

- endpoint list
- request examples
- response examples
- error format
- authentication method
- pagination/filtering details

---

## 3. Example response patterns

### Success response

```json
{
  "data": {
    "id": 101,
    "name": "Alice",
    "email": "alice@example.com"
  },
  "meta": {
    "requestId": "5b0c8d8a-5c2f-4a47-87c1-1b8c67d43e33"
  }
}
```

### Error response

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User 101 does not exist"
  },
  "meta": {
    "requestId": "5b0c8d8a-5c2f-4a47-87c1-1b8c67d43e33"
  }
}
```

---

## 4. Recommended conventions

### Naming

- use plural nouns: `users`, `orders`, `payments`
- use lowercase and hyphen/standard URL style consistently
- avoid verbs in endpoint names where REST semantics are enough

### Query parameters

- `page`, `limit`
- `sort`
- `search`
- domain filters like `status`, `category`, `type`

### JSON fields

- keep names consistent: `createdAt` everywhere, or `created_at` everywhere
- do not mix styles randomly

---

## 5. Common mistakes

- returning `200 OK` for every result, even failures
- inconsistent response structure across endpoints
- using `POST` for everything
- exposing internal DB field names without thought
- no pagination on list endpoints
- no validation
- undocumented breaking changes
- vague error messages

---

## 6. Minimal API checklist

Use this checklist during design reviews:

- [ ] Are endpoints resource-oriented?
- [ ] Are names consistent?
- [ ] Are HTTP methods correct?
- [ ] Are status codes meaningful?
- [ ] Is validation defined?
- [ ] Is error format standardized?
- [ ] Is pagination/filtering supported where needed?
- [ ] Is versioning strategy clear?
- [ ] Is security addressed?
- [ ] Is observability included?
- [ ] Is documentation ready?

---

## 7. Python demo included

This package includes a small Flask application that demonstrates:

- versioned endpoints under `/v1`
- CRUD for users
- pagination and search
- validation
- consistent error format
- request ID in responses
- health check endpoint

Files:

- `api_design_principles.md`
- `app.py`
- `requirements.txt`

---

## 8. Run the sample app

```bash
pip install -r requirements.txt
python app.py
```

Then test:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/v1/users
curl -X POST http://127.0.0.1:5000/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@example.com"}'
```

---

## 9. One-line summary

A good API is **simple, consistent, predictable, secure, observable, and easy to evolve**.
