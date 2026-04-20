import os

from flask import Flask, jsonify, request
from opensearchpy import OpenSearch

app = Flask(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "query-service")
PORT = int(os.getenv("FLASK_PORT", "8003"))
OPENSEARCH_URL = os.getenv("OPENSEARCH_URL", "http://opensearch:9200")
INDEX_NAME = os.getenv("OPENSEARCH_INDEX", "orders_read")

client = OpenSearch(
    hosts=[OPENSEARCH_URL],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
)


@app.get("/health")
def health():
    return jsonify({"status": "UP", "service": SERVICE_NAME})


@app.get("/query/orders/<order_id>")
def get_order(order_id: str):
    try:
        response = client.get(index=INDEX_NAME, id=order_id)
        return jsonify(response["_source"])
    except Exception as exc:
        return jsonify({"error": "Order not found", "details": str(exc)}), 404


@app.get("/query/orders")
def list_orders():
    status = request.args.get("status")
    customer_id = request.args.get("customer_id")
    size = min(int(request.args.get("size", 25)), 100)

    filters = []
    if status:
        filters.append({"term": {"status.keyword": status}})
    if customer_id:
        filters.append({"term": {"customer_id.keyword": customer_id}})

    query = {
        "size": size,
        "sort": [{"created_at": {"order": "desc"}}],
        "query": {"bool": {"filter": filters}} if filters else {"match_all": {}},
    }
    result = client.search(index=INDEX_NAME, body=query)
    return jsonify([hit["_source"] for hit in result["hits"]["hits"]])


@app.get("/query/orders/search")
def search_orders():
    q = request.args.get("q", "")
    status = request.args.get("status")
    must = []
    filters = []

    if q:
        must.append(
            {
                "multi_match": {
                    "query": q,
                    "fields": ["customer_name^2", "item^3", "status", "search_text"],
                }
            }
        )
    if status:
        filters.append({"term": {"status.keyword": status}})

    if not must:
        must = [{"match_all": {}}]

    query = {
        "size": 25,
        "sort": [{"created_at": {"order": "desc"}}],
        "query": {"bool": {"must": must, "filter": filters}},
    }
    result = client.search(index=INDEX_NAME, body=query)
    return jsonify([hit["_source"] for hit in result["hits"]["hits"]])


@app.get("/query/dashboard/status-counts")
def status_counts():
    query = {
        "size": 0,
        "aggs": {
            "by_status": {
                "terms": {"field": "status.keyword", "size": 10}
            }
        },
    }
    result = client.search(index=INDEX_NAME, body=query)
    buckets = result["aggregations"]["by_status"]["buckets"]
    return jsonify([{"status": bucket["key"], "count": bucket["doc_count"]} for bucket in buckets])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
