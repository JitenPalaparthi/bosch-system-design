import os
from fastapi import FastAPI, HTTPException, Query
from opensearchpy import OpenSearch


OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "products")

client = OpenSearch(
    hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False,
)

app = FastAPI(title="CQRS Read API", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "read-api"}


@app.get("/products")
def list_products():
    body = {
        "query": {"match_all": {}},
        "sort": [{"id": {"order": "asc"}}],
        "size": 100,
    }
    try:
        result = client.search(index=OPENSEARCH_INDEX, body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/products/search")
def search_products(q: str = Query(..., min_length=1)):
    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["name^3", "description", "category^2"],
            }
        },
        "size": 100,
    }
    try:
        result = client.search(index=OPENSEARCH_INDEX, body=body)
        return [hit["_source"] for hit in result["hits"]["hits"]]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        result = client.get(index=OPENSEARCH_INDEX, id=product_id)
        return result["_source"]
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Product not found in read model: {exc}") from exc
