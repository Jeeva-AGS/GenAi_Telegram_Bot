import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from rag import index_folder, answer_query
from storage import init_db, get_user_history, set_user_history
from typing import List
from dotenv import load_dotenv
load_dotenv()

from vision import describe_image

# config env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
DOCS_FOLDER = os.getenv("DOCS_FOLDER", "example_docs")


# init DB on startup
init_db()

# history
def push_history(user_id: str, entry: str):
    existing = get_user_history(user_id)
    if existing:
        hist = json.loads(existing)
    else:
        hist = []
    hist.append(entry)
    hist = hist[-3:]
    set_user_history(user_id, json.dumps(hist))

def get_history(user_id: str) -> List[str]:
    existing = get_user_history(user_id)
    return json.loads(existing) if existing else []

# handlers
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi!!! im a Chat BOT trained using your knowledge . use below commands to interact with me ,\n\n"
        "/ask <query>  :: ask Question related to uploaded Documents \n"
        "/summarize    :: summarize your last 3 messages\n"
        "/myid         :: to get your telegram user id\n"
        "/help         :: this message\n\n"
        "for generating description for image just upload the image (our bot will auto detect it) \n\n"

        "/index        :: (admin only) if your getting No documents indexed, run this command - [ before that , check if there is files in this folder (example_docs/) ]\n"
    )

async def index_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_USER_ID and str(update.effective_user.id) != str(ADMIN_USER_ID):
        await update.message.reply_text("Only admin can run /index.")
        return
    await update.message.reply_text("Indexing files... this will take a moment.")
    loop = asyncio.get_event_loop()
    n = await loop.run_in_executor(None, index_folder, DOCS_FOLDER)
    await update.message.reply_text(f"Indexed {n} files from {DOCS_FOLDER}.")

async def ask_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    query = " ".join(context.args)
    user_id = str(update.effective_user.id)
    push_history(user_id, "Q: " + (query if len(query) < 300 else query[:300] + "..."))
    await update.message.chat.send_action(action="typing")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, answer_query, query, 3)
    answer = result["answer"]
    sources = result["sources"]
    cached = result["cached"]
    push_history(user_id, "A: " + (answer[:300] + ("..." if len(answer) > 300 else "")))
    reply = ""
    if cached:
        reply += "(cached)\n"
    reply += answer + "\n\nSOURCES: " + (", ".join(sources) if sources else "none")
    await update.message.reply_text(reply)

async def summarize_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    hist = get_history(user_id)
    if not hist:
        await update.message.reply_text("No history for you yet.")
        return
    summary_prompt = "Summarize the following into 3 concise bullet points:\n\n" + "\n".join(hist)
    push_history(user_id, "SYS: summarize request")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, answer_query, summary_prompt, 1)
    await update.message.reply_text(result["answer"])

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    txt = update.message.text
    push_history(user_id, "MSG: " + (txt[:300] + ("..." if len(txt) > 300 else "")))
    await update.message.reply_text("Hey Hi, Hope you doing Good \n use /help command to get more info about me.")

async def show_id(update, context):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Your Telegram User ID is: {user_id} \n dont share it with anyone or they will use me as a puppet :(")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    tg_file = await context.bot.get_file(file_id)

    save_path = f"temp_{file_id}.jpg"
    await tg_file.download_to_drive(save_path)
    await update.message.chat.send_action(action="typing")

    caption , tags = describe_image(save_path)

    reply = f"\t IMAGE DESCRIPTION \n\n"\
            f"{caption}\n\n"\
            f"**Tags** : {', '.join(tags)}"
    
    await update.message.reply_markdown(reply)


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Set TELEGRAM_TOKEN environment variable (see README).")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("index", index_cmd))
    app.add_handler(CommandHandler("ask", ask_cmd))
    app.add_handler(CommandHandler("summarize", summarize_cmd))
    app.add_handler(CommandHandler("myid", show_id))
    app.add_handler(MessageHandler(filters.PHOTO,handle_image))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))

    print("Starting Mini-RAG bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
