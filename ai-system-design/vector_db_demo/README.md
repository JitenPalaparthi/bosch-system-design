# Vector Database End-to-End Demo using Docker Compose

This project shows a **complete vector database flow**:

1. Start a vector database with Docker Compose
2. Start an API service that uses an embedding model
3. Load sample documents into the vector DB
4. Run semantic search queries
5. See how metadata filtering works

The stack is intentionally simple and demo-friendly:

- **Qdrant** as the vector database
- **FastAPI** as the application/API layer
- **Sentence Transformers** for embeddings
- **Docker Compose** for one-command startup

---

## Architecture

```text
Sample Documents
      ↓
Embedding Model (all-MiniLM-L6-v2)
      ↓
Qdrant Vector Database
      ↓
FastAPI Search API
      ↓
User Query → Query Embedding → Similarity Search → Results
```

---

## What this demo teaches

- what a vector database stores
- how text becomes embeddings
- how vectors are indexed and searched
- how top-K semantic retrieval works
- how metadata filtering changes results
- how an application integrates with a vector DB

---

## Project Structure

```text
vector_db_demo/
├── docker-compose.yml
├── README.md
├── app/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── main.py
│   └── requirements.txt
└── data/
    └── sample_docs.json
```

---

## Prerequisites

- Docker
- Docker Compose

---

## Start the demo

From the project directory:

```bash
docker compose up --build
```

This starts:

- Qdrant on `http://localhost:6333`
- API server on `http://localhost:8000`

---

## Step 1: Check health

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok","points_count":0}
```

---

## Step 2: Load sample documents

```bash
curl -X POST http://localhost:8000/documents/load-sample
```

Expected:

```json
{"inserted":6,"ids":["doc-1","doc-2","doc-3","doc-4","doc-5","doc-6"]}
```

---

## Step 3: Run a semantic search

### Example: password help

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I change my password?","limit":3}'
```

You should see the **Password Reset Guide** near the top, even though the exact wording is different.

### Example: suspicious emails

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What should I do if I get a suspicious email?","limit":3}'
```

You should see the **Phishing Email Warning** document near the top.

---

## Step 4: Search with metadata filtering

This query searches only within the `security` category:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"remote access rules for laptops","limit":3,"category":"security"}'
```

This demonstrates how vector search and metadata filtering work together.

---

## Step 5: Insert your own documents

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '[
    {
      "title": "API Rate Limit Policy",
      "text": "Clients may send up to 100 requests per minute. Excess traffic will receive HTTP 429 responses.",
      "category": "api",
      "source": "manual",
      "metadata": {"team": "platform"}
    }
  ]'
```

Then search:

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What happens if I send too many requests?","limit":3}'
```

---

## API Endpoints

### `GET /`
Basic service info.

### `GET /health`
Checks collection status.

### `GET /collections/info`
Returns Qdrant collection stats.

### `POST /documents/load-sample`
Loads the bundled sample documents.

### `POST /documents`
Upserts custom documents.

### `POST /search`
Runs semantic similarity search.

Request body:

```json
{
  "query": "How do I reset my password?",
  "limit": 5,
  "category": "support"
}
```

---

## End-to-End Internal Flow

### 1. Documents arrive
You send documents to the API.

### 2. Embeddings are generated
The app uses:

- `sentence-transformers/all-MiniLM-L6-v2`

Each document text becomes a 384-dimensional vector.

### 3. Vectors are stored in Qdrant
Each stored point contains:

- ID
- vector
- payload (title, text, category, source, metadata)

### 4. Query arrives
A user sends a plain-English search query.

### 5. Query embedding is generated
The same embedding model converts the query into a vector.

### 6. Similarity search runs
Qdrant compares the query vector with stored document vectors using cosine similarity.

### 7. Top-K matches are returned
The API returns the nearest semantic matches with scores.

---

## Key Vector Database Concepts Demonstrated

### Embeddings
Text is mapped into dense vectors.

### Vector Storage
Qdrant stores vectors and payloads together.

### Similarity Search
Search is based on meaning, not exact keywords.

### Top-K Retrieval
Only the closest results are returned.

### Metadata Filtering
Results can be restricted by category or other metadata.

---

## How this relates to RAG

This demo is the **retrieval half** of a RAG system.

RAG flow:

```text
Documents → Chunking → Embeddings → Vector DB
User Query → Embedding → Retrieve Relevant Chunks → LLM → Answer
```

This project covers:

- document storage
- embeddings
- vector retrieval
- metadata filtering

To convert it into full RAG, you would add:

- chunking for large documents
- reranking (optional)
- prompt builder
- LLM generation layer

---

## Common Extensions

You can extend this demo by adding:

- Streamlit or React UI
- OpenAI / Ollama / vLLM generation layer
- chunking pipeline for PDFs
- reranker model
- hybrid search (BM25 + vector)
- PostgreSQL + pgvector version
- OpenSearch version
- Kafka ingestion pipeline
- authentication and multi-tenant filters

---

## Troubleshooting

### The first startup is slow
The embedding model is downloaded on first run.

### No results returned
Make sure you loaded sample documents first:

```bash
curl -X POST http://localhost:8000/documents/load-sample
```

### Rebuild cleanly

```bash
docker compose down -v
docker compose up --build
```

---

## Stop the demo

```bash
docker compose down
```

To also remove Qdrant data volume:

```bash
docker compose down -v
```

---

## Summary

This demo gives you a practical, end-to-end example of a vector database in action:

- Docker Compose spins up the stack
- documents are embedded
- vectors are stored in Qdrant
- queries are semantically matched
- metadata filters refine results

It is small enough for learning, but structured like a real retrieval service.
