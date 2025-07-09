# main.py

import os
import sys
import importlib
import logging
import tempfile
from dotenv import load_dotenv
from telegram import Update, Chat, Message
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from aicore import AICore
import session_manager

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in .env")
    sys.exit(1)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext._application").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❗ Unhandled error: {context.error}")

def load_commands(application: Application):
    commands_path = os.path.join(os.path.dirname(__file__), "command")
    for file in os.scandir(commands_path):
        if file.name.endswith(".py") and not file.name.startswith("__"):
            modulename = f"command.{file.name[:-3]}"
            try:
                module = importlib.import_module(modulename)
                if hasattr(module, "command") and hasattr(module, "run"):
                    handler = CommandHandler(module.command, module.run)
                    application.add_handler(handler)
                    print(f"✔ Loaded command: /{module.command}")
                else:
                    print(f"⚠️ Skipped: {file.name} (missing 'command' or 'run')")
            except Exception as e:
                print(f"❌ Failed to load {file.name}: {e}")

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    load_commands(application)
    application.add_error_handler(global_error_handler)

    try:
        from utils.dlpsendmusic import download_and_send_music
        application.add_handler(
            CallbackQueryHandler(download_and_send_music, pattern=r"^sendmusic:")
        )
        print("🎯 Callback handler for sendmusic loaded")
    except Exception as e:
        print(f"❌ Failed to load callback handler: {e}")

    ai = AICore()

    async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        try:
            message_text = update.message.text or update.message.caption or ""
            reply_message: Message = update.message.reply_to_message
            if reply_message and reply_message.from_user.id == context.bot.id:
                message_text = reply_message.text

            is_group = update.effective_chat.type in ["group", "supergroup"]
            user_id = update.effective_user.id

            session = session_manager.get_session(user_id, is_group=is_group)

            if update.message.photo:
                photo = update.message.photo[-1]
                file = await photo.get_file()
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
                    await file.download_to_drive(temp_img.name)
                    result = ai.chat_with_image(message_text, temp_img.name, history=session)
            else:
                result = ai.chat(message_text, history=session)

            session.append({"role": "user", "content": message_text})
            session.append({"role": "assistant", "content": result})

            session_manager.update_session(
                user_id=user_id,
                prompt=message_text,
                response=result,
                is_group=is_group,
                username=update.effective_user.username,
                sendername=update.effective_user.full_name,
                msgtype=update.effective_chat.type,
                groupid=str(update.effective_chat.id)
            )

            await update.message.reply_text(result)

        except Exception as e:
            logger.error(f"❌ Error AI handler: {e}")
            await update.message.reply_text("⚠️ An error occurred while processing the message.")

    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_ai_message))
    print("💬 AI message handler loaded")

    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()