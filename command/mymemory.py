# command/mymemory.py

from telegram import Update
from telegram.ext import ContextTypes
import session_manager

command = "mymemory"

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ This command can only be used in private chat to protect your privacy.")
        return

    user_id = update.effective_user.id
    db = session_manager.load_db(is_group=False)
    key = str(user_id)

    if key not in db or not db[key].get("memory"):
        await update.message.reply_text("🤖 I don't have any personal information about you yet.")
        return

    memory = db[key]["memory"]
    text_lines = ["🧠 This is what I remember about you:\n"]

    for k, v in memory.items():
        text_lines.append(f"• {k}: {v}")

    await update.message.reply_text("\n".join(text_lines))