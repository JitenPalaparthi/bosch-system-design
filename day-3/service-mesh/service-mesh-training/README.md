# Service Mesh Training Demo

This package explains **what a service mesh is**, the **main types / implementation styles**, and gives a **small Python + Envoy training simulation** using **Docker Compose**.

---

## 1) What is a service mesh?

A **service mesh** is an infrastructure layer for **service-to-service communication** in a microservices system.

Instead of putting networking logic inside every service, the mesh moves that logic into a dedicated layer, usually proxies. That layer can handle:

- service discovery
- traffic routing
- retries
- timeouts
- circuit breaking
- observability
- service identity and mTLS
- access control and policy enforcement

### Simple idea

Without mesh:

```text
Service A ----------------------> Service B
```

With mesh:

```text
Service A -> Proxy/Sidecar A -> Proxy/Sidecar B -> Service B
```

So the application code focuses on **business logic**, while the mesh handles **network behavior and policy**.

---

## 2) Why do we use a service mesh?

In small systems, direct service-to-service communication is manageable.

In large microservice systems, the following problems appear quickly:

- every team implements retries differently
- security is inconsistent
- traffic policies are duplicated
- telemetry is scattered
- debugging cross-service calls becomes hard
- rollout strategies like canary or traffic splitting are difficult

A service mesh solves these concerns in a **centralized and consistent** way.

---

## 3) Core parts of a service mesh

### Data plane
The **data plane** is the part that actually carries traffic.

Usually this means:

- sidecar proxies such as Envoy, or
- node-level proxies / tunnel processes

### Control plane
The **control plane** configures the data plane.

It pushes:

- routing rules
- certificates
- security policies
- telemetry configuration
- traffic rules

### Diagram

```text
                    +---------------------------+
                    |        Control Plane      |
                    | config, policy, identity  |
                    +-------------+-------------+
                                  |
                                  v
      +----------------+    +----------------+    +----------------+
      | Service A      |    | Service B      |    | Service C      |
      | + Proxy A      |<-->| + Proxy B      |<-->| + Proxy C      |
      +----------------+    +----------------+    +----------------+

Data Plane  = proxies moving traffic
Control Plane = component configuring proxies
```

---

## 4) Types of service mesh

There is no single universal "official" taxonomy, but in practice teams commonly discuss service mesh by **data-plane style**.

### Type 1: Sidecar-based service mesh

Each workload gets its own proxy sidecar.

```text
Pod / Container Group
+--------------------------------+
| App Container  | Proxy Sidecar |
+--------------------------------+
```

#### Characteristics
- most widely known model
- very flexible
- good traffic control and observability
- extra resource overhead per workload
- more moving parts

#### Examples
- Istio in sidecar mode
- Consul service mesh with Envoy sidecars
- Linkerd sidecar model

---

### Type 2: Sidecarless / ambient / transparent mesh

The application does not get a proxy sidecar attached to every workload. Instead, the mesh moves traffic handling into shared infrastructure components.

```text
App A ----> node/tunnel layer ----> node/tunnel layer ----> App B
```

#### Characteristics
- lower per-pod overhead
- simpler app onboarding in some cases
- different operational model
- may split L4 and L7 features across different components

#### Examples
- Istio ambient mode

---

### Type 3: Library-based or embedded communication layer

Some architectures do not use standalone sidecar proxies. Instead, communication features are embedded into SDKs, client libraries, or framework-level networking layers.

```text
Service A [mesh logic in library] ----> Service B [mesh logic in library]
```

#### Characteristics
- can reduce proxy overhead
- often tighter coupling to language/runtime
- less language-neutral than proxy-based approaches
- not always marketed as a full modern service mesh, but useful as a conceptual contrast in training

---

## 5) Popular service mesh products

### Istio
Very feature-rich. Strong traffic management, policy, security, and observability. Supports sidecar mode and ambient mode.

### Linkerd
Known for simplicity and operational ease. Often chosen when teams want a lighter mesh experience.

### Consul service mesh
Good when service networking, service discovery, and hybrid infrastructure are all important.

---

## 6) API Gateway vs Service Mesh

These are related, but different.

### API Gateway
Usually handles **north-south traffic**:

```text
Client -> API Gateway -> Internal Services
```

Common concerns:
- auth for external consumers
- rate limiting
- request transformation
- versioned public APIs

### Service Mesh
Usually handles **east-west traffic**:

```text
Service A -> Service B -> Service C
```

Common concerns:
- retries
- timeouts
- mTLS
- service identity
- telemetry

---

## 7) What this training demo shows

This demo is not a full production mesh. It is a **simulation** that teaches the central idea:

- `app1` is a Python service
- `app2` is another Python service
- `envoy1` acts like the outbound sidecar for `app1`
- `envoy2` acts like the inbound sidecar for `app2`
- traffic goes through Envoy instead of direct app-to-app communication

### Topology

```text
Browser / curl
     |
     v
 app1:5000
     |
     v
 envoy1:15001  --------->  envoy2:15002  --------->  app2:5001
(outbound proxy)           (inbound proxy)            (target app)
```

---

## 8) Project structure

```text
service-mesh-training/
├── docker-compose.yml
├── README.md
├── app1/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── app2/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── envoy1/
│   └── envoy.yaml
└── envoy2/
    └── envoy.yaml
```

---

## 9) Python applications

### app1
Responsibilities:
- receives HTTP requests from the user
- calls `app2` through `envoy1`
- returns the downstream result as JSON

Endpoints:
- `GET /`
- `GET /call`

### app2
Responsibilities:
- serves the downstream response
- can simulate delay
- can simulate failure to demonstrate retry/timeout behavior

Endpoints:
- `GET /`
- `GET /hello`

Environment flags in `app2`:
- `FAILURE_RATE`: integer percentage, for example `30`
- `DELAY_MS`: integer delay in milliseconds

---

## 10) Envoy role in this demo

### envoy1
Acts as outbound proxy for `app1`.

Configured to:
- receive traffic on port `15001`
- route traffic to `envoy2`
- apply timeout
- apply retry policy

### envoy2
Acts as inbound proxy for `app2`.

Configured to:
- receive traffic on port `15002`
- forward to local `app2:5001`

This is enough to demonstrate the essence of a sidecar-based mesh flow.

---

## 11) Docker Compose setup

This project uses Docker Compose only for training convenience.

Services:
- `app1`
- `app2`
- `envoy1`
- `envoy2`

All services are attached to the `mesh-net` bridge network.

---

## 12) How to run

From the project root:

```bash
docker compose up --build
```

### Test the services

```bash
curl http://localhost:5000/
curl http://localhost:5000/call
```

Expected behavior:

- `/` shows that `app1` is running
- `/call` sends a request through the Envoy chain and returns the final payload from `app2`

---

## 13) Request flow explanation

When you call:

```bash
curl http://localhost:5000/call
```

The request path is:

1. Request enters `app1`
2. `app1` sends HTTP request to `envoy1`
3. `envoy1` applies route rules, timeout, and retry policy
4. `envoy1` forwards request to `envoy2`
5. `envoy2` forwards request to `app2`
6. `app2` returns response
7. Response goes back through `envoy2` and `envoy1`
8. `app1` returns the combined JSON to the caller

---

## 14) Training experiments

### Experiment A: Retry behavior

In `docker-compose.yml`, change:

```yaml
FAILURE_RATE: 0
```

to:

```yaml
FAILURE_RATE: 40
```

Then restart:

```bash
docker compose up --build
```

Now `app2` will fail some requests. Envoy retry policy may recover transient failures.

---

### Experiment B: Timeout behavior

In `docker-compose.yml`, change:

```yaml
DELAY_MS: 0
```

to:

```yaml
DELAY_MS: 3000
```

Because Envoy timeout is set to `2s`, the request should fail faster instead of waiting forever.

---

### Experiment C: Observe Envoy stats

```bash
curl http://localhost:9901/stats
curl http://localhost:9902/stats
```

This helps explain observability in a proxy-based architecture.

---

## 15) What this demo does not include

To keep the example simple, this package does **not** implement:

- real mTLS certificates
- distributed tracing backend
- centralized control plane
- automatic service discovery from Kubernetes
- advanced traffic splitting or canary rollout

In production, those are usually handled by a full mesh platform such as Istio, Linkerd, or Consul.

---

## 16) Real-world talking points for training

Use these messages in class:

### Point 1
A service mesh is about **standardizing operational communication behavior** between services.

### Point 2
The mesh usually handles **east-west traffic**, while API gateways usually handle **north-south traffic**.

### Point 3
The biggest value appears when the number of services grows and cross-cutting networking concerns become repetitive.

### Point 4
A sidecar mesh gives strong control and visibility, but it also adds operational overhead.

### Point 5
Newer models such as ambient / sidecarless meshes try to reduce that overhead.

---

## 17) Quick summary

A service mesh gives you:

- reliability
- observability
- security
- policy control
- traffic management

This demo helps learners understand the main idea without requiring Kubernetes.

