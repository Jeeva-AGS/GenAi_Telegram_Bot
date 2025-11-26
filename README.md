Mini-RAG Telegram Bot
=====================

Overview
--------
Lightweight Telegram bot that answers questions using a small local knowledge base.
Features:
- /ask <query> — retrieve answer from indexed documents (RAG)
- /index — index files in example_docs/
- /summarize — summarize last 3 interactions for the user
- Basic caching and message history

Quick start
-----------
1. Create a venv and install:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Put 3–5 .md or .txt files into example_docs/

3. Set environment variables:
   export TELEGRAM_TOKEN="your_telegram_bot_token"
   export GROQ_API_KEY="your_GROQ_key"   # optional - recommended
   # optional:
   export EMBED_MODEL="all-MiniLM-L6-v2"
   export OPENAI_MODEL="gpt-3.5-turbo"

4. Run:
   python app.py

5. In Telegram:
   - /index
   - /ask What is the vacation policy?   (example)
   - /summarize

