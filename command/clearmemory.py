# command/clearmemory.py

from telegram import Update
from telegram.ext import ContextTypes
import session_manager

command = "clearmemory"

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ This command can only be used in private chat to protect your privacy.")
        return

    user_id = update.effective_user.id
    db = session_manager.load_db(is_group=False)
    key = str(user_id)

    if key in db and "memory" in db[key]:
        db[key]["memory"] = {}
        session_manager.save_db(db, is_group=False)
        await update.message.reply_text("✅ All your personal memories have been deleted.")
    else:
        await update.message.reply_text("⚠️ All your personal memories have been deleted.")