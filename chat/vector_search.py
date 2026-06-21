from __future__ import annotations

import os
import math
from typing import Any, Dict, List

from .models import PDFDocument
from .llm import generate_llm_response

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "student_data")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
VECTOR_DIMENSION = 1536
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

try:
    import openai
except ImportError:
    openai = None

try:
    qdrant_module = __import__("qdrant_client")
    QdrantClient = getattr(qdrant_module, "QdrantClient")
    qdrant_models = __import__("qdrant_client.http.models", fromlist=["VectorParams", "Distance", "PointStruct"])
    VectorParams = getattr(qdrant_models, "VectorParams")
    Distance = getattr(qdrant_models, "Distance")
    PointStruct = getattr(qdrant_models, "PointStruct")
except ImportError:
    QdrantClient = None
    VectorParams = None
    Distance = None
    PointStruct = None


def is_vector_search_enabled() -> bool:
    return (
        QdrantClient is not None
        and openai is not None
        and bool(QDRANT_URL)
        and bool(OPENAI_API_KEY)
    )


def _ensure_openai() -> None:
    if openai is None:
        raise RuntimeError("openai package is not installed. Install it with `pip install openai`.")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured.")
    openai.api_key = OPENAI_API_KEY


def init_qdrant_client() -> Any:
    if QdrantClient is None:
        raise RuntimeError("qdrant-client package is not installed. Install it with `pip install qdrant-client`.")

    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None, prefer_grpc=False)


def ensure_collection(client: Any) -> None:
    try:
        client.get_collection(collection_name=QDRANT_COLLECTION)
    except Exception:
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors=VectorParams(size=VECTOR_DIMENSION, distance=Distance.COSINE),
        )


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = max(end - overlap, end)
    return chunks


def embed_text(text: str) -> List[float]:
    _ensure_openai()
    response = openai.Embedding.create(model=EMBEDDING_MODEL, input=text)
    return response["data"][0]["embedding"]


def index_document(client: Any, doc) -> None:
    student_no = doc.file_name.replace(".pdf", "")
    chunks = chunk_text(doc.content)
    points = []

    for index, chunk in enumerate(chunks):
        vector = embed_text(chunk)
        payload = {
            "file_name": doc.file_name,
            "student_no": student_no,
            "chunk_id": index,
            "content_snippet": chunk[:1200],
        }
        points.append(PointStruct(id=f"{student_no}-{index}", vector=vector, payload=payload))

    if points:
        client.upsert(collection_name=QDRANT_COLLECTION, points=points)


def index_all_documents() -> None:
    if not is_vector_search_enabled():
        raise RuntimeError("Vector search is not configured. Set QDRANT_URL and OPENAI_API_KEY and install the required packages.")

    client = init_qdrant_client()
    ensure_collection(client)

    for doc in PDFDocument.objects.all():
        index_document(client, doc)


def qdrant_search(query: str, top_k: int = 5) -> List[Dict]:
    if not is_vector_search_enabled():
        return []

    client = init_qdrant_client()
    ensure_collection(client)

    query_vector = embed_text(query)
    search_results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    hits = []
    for item in search_results:
        payload = item.payload or {}
        hits.append(
            {
                "score": item.score,
                "file_name": payload.get("file_name", "Unknown"),
                "student_no": payload.get("student_no", "Unknown"),
                "snippet": payload.get("content_snippet", ""),
                "chunk_id": payload.get("chunk_id", 0),
            }
        )

    return hits


def generate_ai_response(user_input: str, hits: List[Dict]) -> str:
    _ensure_openai()
    records = []
    included_students = set()

    for hit in hits:
        student_no = hit.get("student_no")
        snippet = hit.get("snippet", "")
        if student_no not in included_students:
            included_students.add(student_no)
            records.append(f"Student {student_no} excerpt:\n{snippet}")

    if not records:
        return "🤖 I couldn't find relevant student data for that query."

    system_prompt = (
        "You are a helpful academic assistant. Use only the provided student transcripts and profile excerpts "
        "to answer the user's question. If the question asks for a specific student, mention that student's roll number clearly. "
        "If the answer is not supported by the provided records, say that you do not have enough information. "
        "For example, if the user asks 'Which semester was my best?', answer with the best semester and SGPA."
    )

    user_prompt = (
        "Student records:\n"
        + "\n\n".join(records)
        + "\n\nQuestion: "
        + user_input
        + "\n\nAnswer:"
    )

    return generate_llm_response(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=420,
    )
