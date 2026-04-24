# Email Spam RAG Demo (Docker Compose)

This is a small end-to-end **RAG demo** that classifies suspicious emails using:

- **FastAPI** for the API
- **ChromaDB** as the local vector store
- **Sentence Transformers** for embeddings
- **FLAN-T5 Small** as a lightweight local text generation model
- **Docker Compose** to run the full stack

## What this demo shows

This demo is meant for training, architecture explanation, and proof-of-concept walkthroughs.

It demonstrates:

1. document ingestion
2. embedding generation
3. vector indexing
4. semantic retrieval
5. prompt construction
6. answer generation with sources

## Architecture

```text
Sample Emails / Security Guidelines
          ↓
      ingest.py
          ↓
 SentenceTransformer embeddings
          ↓
       ChromaDB
          ↓
      FastAPI /ask
          ↓
 retrieve top-k examples
          ↓
 build prompt with context
          ↓
 FLAN-T5 generates answer
```

## Project structure

```text
rag_email_demo/
├── docker-compose.yml
├── README.md
├── data/
│   └── emails.json
└── app/
    ├── Dockerfile
    ├── requirements.txt
    ├── ingest.py
    └── main.py
```

## Run

```bash
docker compose up --build
```

First run can take some time because models are downloaded.

## Health check

```bash
curl http://localhost:8000/health
```

## Example questions

```bash
curl http://localhost:8000/examples
```

## Ask endpoint

### Example 1: classify a suspicious email

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Is this email likely spam? Subject: Urgent payroll correction required. Body: Please send your bank details today to avoid salary delay.",
    "top_k": 4
  }'
```

### Example 2: retrieve only spam-like examples

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why is this message suspicious? Subject: You won a gift card. Body: Confirm your password to release the reward.",
    "top_k": 3,
    "label_filter": "spam"
  }'
```

### Example 3: legitimate email example

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show a legitimate internal HR email example.",
    "top_k": 3,
    "label_filter": "ham"
  }'
```

## Expected response shape

```json
{
  "answer": "Classification: spam ...",
  "retrieved_sources": [
    {
      "id": "email-001",
      "label": "spam",
      "subject": "Urgent payroll correction required",
      "sender": "payroll-update@secure-payroll-help.com",
      "snippet": "Type: spam From: ..."
    }
  ],
  "prompt_used": "..."
}
```

## Why this is good for demo/training

- easy to explain
- single command startup
- shows true RAG flow
- no external paid APIs required
- enough realism to discuss retrieval, chunking, prompting, and hallucination control

## Important limitations

- this is a demo, not production email security
- dataset is intentionally small
- FLAN-T5 Small is lightweight, so answers are basic
- for production, add reranking, more data, ACLs, observability, and better evaluation

## How to extend

1. Add a Streamlit UI
2. Replace FLAN-T5 with Ollama or vLLM
3. Add reranking
4. Switch to OpenSearch / pgvector / Qdrant
5. Ingest real exported emails or helpdesk tickets
6. Add chunking per email body / thread / policy document
7. Add feedback and evaluation metrics

## Demo talking points

- **Ingestion pipeline**: JSON docs are indexed into ChromaDB
- **Retriever**: semantic search finds similar past examples and guidance
- **Generator**: a small local LLM uses retrieved context to explain the decision
- **Grounding**: the response includes retrieved source examples
- **Production path**: swap in larger corpora, better models, policy filters, and monitoring
