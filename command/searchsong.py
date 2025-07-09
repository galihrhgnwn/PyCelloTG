# command/searchsong.py

command = "song"

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ytmusicapi import YTMusic
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

from utils.aisearchsong import generate_ai_slang

ytmusic = YTMusic()

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ You gotta type the song name.\nExample: /searchsong let her go"
        )
        return

    query = " ".join(context.args)
    start_time = time.time()

    message = await update.message.reply_text(
        f"🔍 Searching for song: <i>{query}</i>...", parse_mode="HTML"
    )

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor()

    def search_song():
        results = ytmusic.search(query, filter="songs", limit=1)
        return results[0] if results else None

    result = await loop.run_in_executor(executor, search_song)
    elapsed = time.time() - start_time

    if result:
        title = result.get("title", "Unknown Title")
        artists = result.get("artists", [])
        artist_names = ", ".join(a.get("name", "-") for a in artists)
        video_id = result.get("videoId")
        thumbnail_url = result.get("thumbnails", [{}])[0].get("url")
        url = f"https://music.youtube.com/watch?v={video_id}" if video_id else "No link"

        try:
            slang_text = await generate_ai_slang(title, artist_names, elapsed)
        except Exception as e:
            print(f"[AI ERROR] {e}")
            slang_text = f"✅ Found <i>{title}</i> in {elapsed:.2f}s 😎"

        await message.edit_text(slang_text, parse_mode="HTML")

        response = (
            f"🎵 <b>{title}</b>\n"
            f"👤 <i>{artist_names}</i>\n"
            f"🔗 <a href=\"{url}\">Listen on YouTube Music</a>"
        )

        # Simpan data lagu di chat_data[video_id]
        context.chat_data.setdefault("last_tracks", {})[video_id] = {
            "title": title,
            "artist": artist_names
        }

        keyboard = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton("▶️ Send Music", callback_data=f"sendmusic:{video_id}")
        )

        await update.message.reply_text(response, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.edit_text("❌ Song not found.", parse_mode="HTML")