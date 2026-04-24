import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "demo_documents")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA_FILE = os.getenv("DATA_FILE", "/app/data/sample_docs.json")
VECTOR_SIZE = 384  # all-MiniLM-L6-v2

app = FastAPI(title="Vector Database Demo", version="1.0.0")

client = QdrantClient(url=QDRANT_URL)
encoder = SentenceTransformer(EMBEDDING_MODEL)


class DocumentIn(BaseModel):
    id: Optional[str] = None
    title: str
    text: str
    category: str = "general"
    source: str = "manual"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    category: Optional[str] = None


@app.on_event("startup")
def startup_event() -> None:
    wait_for_qdrant()
    ensure_collection()


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "message": "Vector database demo is running.",
        "collection": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "endpoints": [
            "/health",
            "/documents/load-sample",
            "/documents",
            "/search",
            "/collections/info",
        ],
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    try:
        info = client.get_collection(COLLECTION_NAME)
        return {"status": "ok", "points_count": info.points_count}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/collections/info")
def collection_info() -> Dict[str, Any]:
    info = client.get_collection(COLLECTION_NAME)
    return {
        "name": COLLECTION_NAME,
        "status": str(info.status),
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "indexed_vectors_count": info.indexed_vectors_count,
    }


@app.post("/documents")
def upsert_documents(documents: List[DocumentIn]) -> Dict[str, Any]:
    if not documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    payloads = []
    ids = []
    texts = []
    for doc in documents:
        doc_id = doc.id or str(uuid.uuid4())
        ids.append(doc_id)
        texts.append(doc.text)
        payloads.append(
            {
                "title": doc.title,
                "text": doc.text,
                "category": doc.category,
                "source": doc.source,
                "metadata": doc.metadata,
            }
        )

    vectors = encoder.encode(texts, normalize_embeddings=True).tolist()
    points = [
        models.PointStruct(id=doc_id, vector=vector, payload=payload)
        for doc_id, vector, payload in zip(ids, vectors, payloads)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"inserted": len(points), "ids": ids}


@app.post("/documents/load-sample")
def load_sample_documents() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail=f"Sample data file not found: {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)

    docs = [DocumentIn(**doc) for doc in raw_docs]
    return upsert_documents(docs)


@app.post("/search")
def search(req: SearchRequest) -> Dict[str, Any]:
    vector = encoder.encode(req.query, normalize_embeddings=True).tolist()

    query_filter = None
    if req.category:
        query_filter = models.Filter(
            must=[models.FieldCondition(key="category", match=models.MatchValue(value=req.category))]
        )

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=req.limit,
        query_filter=query_filter,
        with_payload=True,
    )

    matches = []
    for hit in results:
        payload = hit.payload or {}
        matches.append(
            {
                "id": hit.id,
                "score": round(hit.score, 4),
                "title": payload.get("title"),
                "text": payload.get("text"),
                "category": payload.get("category"),
                "source": payload.get("source"),
                "metadata": payload.get("metadata", {}),
            }
        )

    return {"query": req.query, "count": len(matches), "matches": matches}


def wait_for_qdrant(timeout: int = 60) -> None:
    start = time.time()
    while True:
        try:
            client.get_collections()
            return
        except Exception:
            if time.time() - start > timeout:
                raise RuntimeError("Qdrant did not become ready in time")
            time.sleep(2)



def ensure_collection() -> None:
    collections = client.get_collections().collections
    existing = {col.name for col in collections}
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
        )
