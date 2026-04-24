import json
import os
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

DATA_FILE = Path('/app/data/emails.json')
CHROMA_DIR = os.getenv('CHROMA_DIR', '/app/chroma_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'email_rag_demo')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')


def build_text(doc: dict) -> str:
    return (
        f"Type: {doc['label']}\n"
        f"From: {doc['from']}\n"
        f"Subject: {doc['subject']}\n"
        f"Body: {doc['body']}\n"
        f"Indicators: {', '.join(doc['indicators'])}\n"
        f"Why: {doc['why']}"
    )


def main():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "RAG demo over labeled email examples and security guidance"},
    )

    docs = json.loads(DATA_FILE.read_text())
    texts, ids, metas = [], [], []
    for doc in docs:
        texts.append(build_text(doc))
        ids.append(doc['id'])
        metas.append({
            'label': doc['label'],
            'sender': doc['from'],
            'subject': doc['subject'],
            'category': doc.get('category', 'example')
        })

    collection.add(documents=texts, ids=ids, metadatas=metas)
    print(f'Indexed {len(ids)} documents into {COLLECTION_NAME}')


if __name__ == '__main__':
    main()
