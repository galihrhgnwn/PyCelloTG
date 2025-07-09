import os
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor

TEMP_FOLDER = "downloads"
COOKIES_FILE = os.path.join("cookies", "cookies.txt")
os.makedirs(TEMP_FOLDER, exist_ok=True)

YDL_OPTS_TEMPLATE = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(TEMP_FOLDER, "%(id)s.%(ext)s"),
    "cookiefile": COOKIES_FILE,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "prefer_ffmpeg": True,
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
}

executor = ThreadPoolExecutor()

def download_audio_by_video_id(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[DEBUG] Downloading audio from: {url}")

    if not os.path.exists(COOKIES_FILE):
        raise FileNotFoundError(f"❌ cookies.txt not found at {COOKIES_FILE}")

    ydl_opts = YDL_OPTS_TEMPLATE.copy()

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
    return filename

async def download_and_send_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🎧 Preparing download...")

    data = query.data  # format: sendmusic:<videoId>

    if not data.startswith("sendmusic:"):
        await query.edit_message_text("❌ Invalid song data.")
        return

    video_id = data[len("sendmusic:"):]
    track_data = context.chat_data.get("last_tracks", {}).get(video_id)

    if not track_data:
        await query.edit_message_text("❌ No song data found.")
        return

    title = track_data["title"]
    artist = track_data["artist"]

    loop = asyncio.get_event_loop()
    filepath = None

    try:
        filepath = await loop.run_in_executor(executor, download_audio_by_video_id, video_id)

        with open(filepath, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                title=title,
                performer=artist,
            )
        print(f"[INFO] Sent song: {title} by {artist}")

    except Exception as e:
        print(f"[ERROR] Failed to send song: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Failed to download and send music.")
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                print(f"[WARN] Failed to clean up {filepath}")