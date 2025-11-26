Mini-RAG Telegram Bot
=====================

https://github.com/user-attachments/assets/c3837b32-f932-4b05-935c-26a770aaa2df

Overview
--------
Lightweight Telegram bot that answers questions using a small local knowledge base we provide.
Features:
- /ask <query> - retrieve answer from indexed documents (RAG)
- /index - index files in example_docs/ (admin only)
- /help - to get help 
- /summarize - summarize last 3 interactions for the user
- /myid - to get your telegram id
- Basic caching and message history

Quick start
-----------
1. Create a venv and install:
   ```bash
   python -m venv venv
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. Put your .md or .pdf or .txt files into example_docs/ folder

3. Set environment variables:

   Create .env and set below variable
   ```bash
   - TELEGRAM_TOKEN="your_telegram_bot_token"
   - GROQ_API_KEY="your_GROQ_key"
   - ADMIN_USER_ID = "your telegram user id"
   ```

4. Run:
   ```bash
   python app.py
   ```

5. In Telegram:
   use commands,
   - /ask questions?
   - /summarize
   - /myid
   - /help
   - /index

Project Structure
-------
```bash
Rag/
│
├── app.py
├── rag.py
├── loader.py
├── storage.py
├── example_docs/
│     ├── doc1.pdf
│     ├── doc2.md
│     ├── doc3.txt
│     └── doc4.pdf
│
└── mini_rag.db          # Auto-created SQLite DB
```


# How to Get Required Keys

## 1. Telegram Bot Token

1. Open Telegram.
2. Search for @BotFather.
3. Start a chat and send:  
   /newbot
4. Give your bot a name and a username (must end with "bot").
5. BotFather will give you a token that looks like:
   123456789:ABCdefXYZ123-abc_9876543210
6. Add this to your .env file:
   TELEGRAM_TOKEN=your_telegram_token_here

---

## 2. Groq API Key

1. Go to https://console.groq.com
2. Create an account or log in.
3. Go to "API Keys".
4. Click "Generate Key".
5. Copy the key.
6. Add it to your .env file:
   GROQ_API_KEY=your_groq_api_key_here

---

## 3. Telegram ADMIN_USER_ID

1. Run your app (example):
   python app.py
2. Open Telegram and send /myid to your bot.
3. The bot will reply with your Telegram User ID.
4. Add it to your .env file:
   ADMIN_USER_ID=your_user_id_here

