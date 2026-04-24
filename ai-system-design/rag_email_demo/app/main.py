import os
from typing import List, Optional

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from fastapi import FastAPI
from pydantic import BaseModel, Field
from transformers import pipeline

CHROMA_DIR = os.getenv('CHROMA_DIR', '/app/chroma_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'email_rag_demo')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
GENERATION_MODEL = os.getenv('GENERATION_MODEL', 'google/flan-t5-small')

app = FastAPI(title='Email RAG Demo', version='1.0.0')

embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(COLLECTION_NAME, embedding_function=embedding_fn)
text2text = pipeline('text2text-generation', model=GENERATION_MODEL)


class AskRequest(BaseModel):
    question: str = Field(..., description='The analyst question or raw suspicious email text.')
    top_k: int = Field(default=4, ge=1, le=8)
    label_filter: Optional[str] = Field(default=None, description='Optional filter: spam or ham')


class Source(BaseModel):
    id: str
    label: str
    subject: str
    sender: str
    snippet: str


class AskResponse(BaseModel):
    answer: str
    retrieved_sources: List[Source]
    prompt_used: str


@app.get('/health')
def health():
    return {'status': 'ok', 'collection': COLLECTION_NAME}


@app.get('/examples')
def examples():
    return {
        'questions': [
            'Is this email likely spam? Subject: Urgent payroll correction needed. Body: Click the attached form and send your bank details immediately.',
            'Why is this email suspicious? Subject: Your account has won a gift card. Body: Confirm credentials to release the reward.',
            'Show an example of a legitimate internal HR email about leave policy.'
        ]
    }


@app.post('/ask', response_model=AskResponse)
def ask(req: AskRequest):
    where = {'label': req.label_filter} if req.label_filter else None
    result = collection.query(
        query_texts=[req.question],
        n_results=req.top_k,
        where=where,
    )

    docs = result['documents'][0]
    metas = result['metadatas'][0]
    ids = result['ids'][0]

    context_blocks = []
    sources = []
    for i, (doc, meta, id_) in enumerate(zip(docs, metas, ids), start=1):
        context_blocks.append(f"[Source {i}]\n{doc}")
        snippet = doc[:220].replace('\n', ' ')
        sources.append(Source(
            id=id_,
            label=meta.get('label', 'unknown'),
            subject=meta.get('subject', 'n/a'),
            sender=meta.get('sender', 'n/a'),
            snippet=snippet,
        ))

    prompt = f"""
You are an email security analyst assistant.
Use only the retrieved context below.
If the question asks whether something is spam, classify it as spam or ham and explain the main indicators.
If evidence is insufficient, say so clearly.

Question:
{req.question}

Retrieved Context:
{'\n\n'.join(context_blocks)}

Return in this format:
Classification: <spam/ham/uncertain>
Reasoning: <2-5 concise bullets in prose>
Recommendation: <one short recommendation>
""".strip()

    output = text2text(prompt, max_new_tokens=220, do_sample=False)[0]['generated_text']
    return AskResponse(answer=output, retrieved_sources=sources, prompt_used=prompt)
