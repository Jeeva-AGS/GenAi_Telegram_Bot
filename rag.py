import os
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from loader import load_text_from_file, text_hash
from storage import (
    init_db, upsert_doc, add_chunk, get_all_chunks, get_doc_name,
    cache_query, get_cached_query
)

from dotenv import load_dotenv
load_dotenv()

from groq import Groq


# embed
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
_model = None
def get_embed_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def embed_texts(texts: List[str]):
    model = get_embed_model()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)


# set groq
LLM_MODE = os.getenv("LLM_MODE", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")



# Chunking
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks



# Indexing
def index_folder(folder: str):
    init_db()

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".pdf", ".md", ".txt"))
    ]

    for fname in files:
        path = os.path.join(folder, fname)
        text = load_text_from_file(path)
        h = text_hash(text)

        doc_id = upsert_doc(fname, path, h)

        chunks = chunk_text(text)
        embs = embed_texts(chunks)

        for i, (chunk, emb) in enumerate(zip(chunks, embs)):
            add_chunk(doc_id, i, emb, chunk)

    return len(files)


# Retrieval
def cosine_sim(a, b) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def retrieve(query: str, top_k: int = 3):
    # query cache
    cached = get_cached_query(query)
    if cached:
        return []

    q_emb = embed_texts([query])[0]
    all_chunks = get_all_chunks()

    scored = []
    for doc_id, chunk_id, emb, chunk_text in all_chunks:
        score = cosine_sim(q_emb, emb)
        scored.append((score, doc_id, chunk_text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]



# Prompt
def build_prompt(query: str, retrieved):
    header = (
        "You are given context snippets. "
        "Use ONLY these to answer. If answer is not in context, say so clearly.\n\n"
    )
    ctx_parts = []
    used_docs = []

    for score, doc_id, chunk in retrieved:
        name = get_doc_name(doc_id) or f"doc_{doc_id}"
        ctx_parts.append(f"---\nSource: {name}\n{chunk}\n")
        if name not in used_docs:
            used_docs.append(name)

    context = "\n".join(ctx_parts)
    prompt = f"{header}Context:\n{context}\n\nUser question: {query}\nAnswer:"
    return prompt, used_docs


# llm setup 
def call_llm(prompt: str, max_tokens: int = 300) -> str:
    if LLM_MODE == "groq" and groq_client:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content.strip()

    return "LLM backend not configured.\n\nPreview:\n" + prompt[:1200]



# llm call
def answer_query(query: str, top_k: int = 3) -> dict:
    cached = get_cached_query(query)
    if cached:
        ans, used_sources = cached
        return {
            "answer": ans,
            "sources": used_sources.split("|") if used_sources else [],
            "cached": True
        }

    retrieved = retrieve(query, top_k)
    if not retrieved:
        return {
            "answer": "No documents indexed. Add files to example_docs/ and run /index.",
            "sources": [],
            "cached": False
        }

    prompt, used_sources = build_prompt(query, retrieved)
    ans = call_llm(prompt)

    cache_query(query, ans, used_sources)
    return {"answer": ans, "sources": used_sources, "cached": False}
