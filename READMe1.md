Mini RAG + Telegram Bot

A tiny Retrieval-Augmented Generation setup that I built to learn how RAG systems actually work under the hood.
It supports:

Loading PDFs / TXT / Markdown

Chunking and embedding documents locally (Sentence Transformers)

Storing everything in a simple SQLite DB

Retrieving top-K relevant chunks

Answering questions using a Groq LLM (llama3)

A Telegram bot interface with /index, /ask, /history

This project intentionally avoids “magic libraries” so I could understand each step clearly.

📁 Project Structure
yourproject/
│
├── app.py               # Telegram bot entrypoint
├── rag.py               # Chunking, embedding, retrieval, LLM call
├── loader.py            # PDF/text loading utilities
├── storage.py           # SQLite DB helpers
├── example_docs/        # Put your PDFs or text files here
│     ├── doc1.pdf
│     ├── doc2.pdf
│     ├── doc3.pdf
│     └── doc4.pdf
│
└── mini_rag.db          # Auto-created SQLite DB

🚀 What This RAG Actually Does

I put documents into example_docs/.

index_folder() reads each file, extracts text (for PDFs using PyPDF), and splits it into overlapping chunks.

Each chunk is embedded using a local model (all-MiniLM-L6-v2).

The embeddings and chunk text are stored in SQLite.

When I ask a question, the query is embedded and compared with all stored embeddings using cosine similarity.

Top-K chunks are stitched into a prompt.

Groq LLM answers based only on those chunks.

Answers are cached so repeat questions are instant.

The Telegram bot sits on top of this RAG.

Everything is simple enough that I can see exactly what is happening at each stage.

🧩 Requirements

Install dependencies:

pip install python-telegram-bot==20.7
pip install sentence-transformers
pip install groq
pip install python-dotenv
pip install pypdf


I used Python 3.10+.

🔑 Environment Variables

Create a .env file in your project root:

TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama3-8b-8192
EMBED_MODEL=all-MiniLM-L6-v2
RAG_DB_PATH=mini_rag.db

How to get these keys
1. Telegram Token

Open Telegram.

Search for @BotFather.

Run /newbot

Give your bot a name + username.

BotFather gives you a token that looks like:

123456789:ABCdefXYZ123-abc_9876543210


Paste it into .env as TELEGRAM_TOKEN.

2. Groq API Key

Go to https://console.groq.com

Create an account

Go to API Keys → Generate Key

Copy it into .env as GROQ_API_KEY.

▶️ Running the Project

Start the bot:

python app.py


On startup, the bot checks if the database has embeddings.
If the DB is empty, it automatically indexes documents from example_docs/.

After that, open Telegram and talk to your bot.

🤖 Telegram Commands
/index

Manually re-index all documents.
Useful after adding or editing files in example_docs/.

/ask your question here

Example:

/ask What are the symptoms discussed in doc2?


The bot:

retrieves relevant chunks

builds a prompt

queries Groq

replies with an answer

shows which files were used

/history

Shows your last N questions and answers (saved inside SQLite).

🧠 How It Works Internally

The RAG pipeline is intentionally small:

loader.py
Reads PDFs/TXT/MD and extracts text.

rag.py
Handles chunking, embeddings, retrieval, prompt construction and LLM call.

storage.py
Manages SQLite tables for documents, embeddings, query cache, user history.

app.py
A minimal Telegram interface that exposes a few commands.

I kept everything as transparent as possible so I can inspect each part or customize it later.

📝 Notes

This is a mini educational RAG, not production ready.

It uses simple cosine similarity over all embeddings (no FAISS, no indexes).

Works great for small collections (5–50 documents).

Easy to expand—for example, adding FAISS, rerankers, or better prompts.