import sqlite3
import pickle
import os
from typing import List, Optional, Tuple

DB_PATH = os.getenv("RAG_DB_PATH", "mini_rag.db")

def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("PRAGMA foreign_keys = ON;")  
    return c

def init_db():
    c = conn()
    cur = c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS docs (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    path TEXT,
                    text_hash TEXT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS chunks (
                    doc_id INTEGER,
                    chunk_id INTEGER,
                    embedding BLOB,
                    chunk_text TEXT,
                    PRIMARY KEY (doc_id, chunk_id),
                    FOREIGN KEY (doc_id) REFERENCES docs(id) ON DELETE CASCADE
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS query_cache (
                    query TEXT PRIMARY KEY,
                    answer TEXT,
                    used_sources TEXT
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS user_history (
                    user_id TEXT PRIMARY KEY,
                    history TEXT
                )""")
    c.commit()
    c.close()

# Docs
def upsert_doc(name: str, path: str, text_hash: str) -> int:
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT OR REPLACE INTO docs (name, path, text_hash) VALUES (?, ?, ?)",
                (name, path, text_hash))
    c.commit()
    row = cur.execute("SELECT id FROM docs WHERE name = ?", (name,)).fetchone()
    c.close()
    return row[0]

def get_all_docs() -> List[tuple]:
    c = conn()
    rows = c.execute("SELECT id, name, path, text_hash FROM docs").fetchall()
    c.close()
    return rows

# Embeddings/chunks
def add_chunk(doc_id: int, chunk_id: int, embedding, chunk_text: str):
    c = conn()
    cur = c.cursor()
    blob = pickle.dumps(embedding.astype("float32"))
    cur.execute("""INSERT OR REPLACE INTO chunks (doc_id, chunk_id, embedding, chunk_text)
                   VALUES (?, ?, ?, ?)""", (doc_id, chunk_id, blob, chunk_text))
    c.commit()
    c.close()

def get_all_chunks() -> List[tuple]:
    c = conn()
    rows = c.execute("SELECT doc_id, chunk_id, embedding, chunk_text FROM chunks").fetchall()
    c.close()
    res = []
    for doc_id, chunk_id, blob, chunk_text in rows:
        emb = pickle.loads(blob)
        res.append((doc_id, chunk_id, emb, chunk_text))
    return res

def get_doc_name(doc_id: int):
    c = conn()
    row = c.execute("SELECT name FROM docs WHERE id = ?", (doc_id,)).fetchone()
    c.close()
    return row[0] if row else None

# Query cache
def cache_query(query: str, answer: str, used_sources: List[str]):
    c = conn()
    c.execute("INSERT OR REPLACE INTO query_cache (query, answer, used_sources) VALUES (?, ?, ?)",
              (query, answer, "|".join(used_sources)))
    c.commit()
    c.close()

def get_cached_query(query: str):
    c = conn()
    row = c.execute("SELECT answer, used_sources FROM query_cache WHERE query = ?", (query,)).fetchone()
    c.close()
    return row if row else None

# User history
def set_user_history(user_id: str, json_text: str):
    c = conn()
    c.execute("INSERT OR REPLACE INTO user_history (user_id, history) VALUES (?, ?)", (user_id, json_text))
    c.commit()
    c.close()

def get_user_history(user_id: str):
    c = conn()
    row = c.execute("SELECT history FROM user_history WHERE user_id = ?", (user_id,)).fetchone()
    c.close()
    return row[0] if row else None
