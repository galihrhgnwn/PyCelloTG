command = "hello"

from telegram import Update
from telegram.ext import ContextTypes

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("yeahhhhh brooooooo")
