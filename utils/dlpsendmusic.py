import os
import time
import asyncio
import subprocess
from telegram import Update
from telegram.ext import ContextTypes

TEMP_FOLDER = "downloads"
COOKIES_FILE = os.path.join("cookies", "cookies.txt")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Max cache duration (in seconds) — 24 hours = 86400 seconds
CACHE_DURATION = 86400

def get_audio_path(video_id: str) -> str:
    return os.path.join(TEMP_FOLDER, f"{video_id}.mp3")

def is_cache_valid(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return False
    last_modified = os.path.getmtime(filepath)
    return (time.time() - last_modified) < CACHE_DURATION

def download_audio_to_mp3(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_path = get_audio_path(video_id)

    print(f"[DEBUG] Downloading: {url}")

    # Remove old file if exists
    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        # Coba pakai library yt_dlp langsung
        import yt_dlp

        ydl_opts = {
            "format": "bestaudio/best",
            "extract_audio": True,
            "audio_format": "mp3",
            "audio_quality": 0,
            "outtmpl": output_path,
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except ImportError:
        # Kalau yt_dlp modul gak ada, fallback ke subprocess
        print("[WARN] yt_dlp library not found, falling back to subprocess...")

        cmd = [
            "yt-dlp", "-x", "--audio-format", "mp3",
            "--audio-quality", "0",  # best quality
            "-o", output_path,
            url
        ]
        if os.path.exists(COOKIES_FILE):
            cmd.insert(-1, "--cookies")
            cmd.insert(-1, COOKIES_FILE)

        subprocess.run(cmd, check=True)

    return output_path

async def download_and_send_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🎧 Preparing your music...")

    data = query.data
    if not data.startswith("sendmusic:"):
        await query.edit_message_text("❌ Invalid request.")
        return

    video_id = data[len("sendmusic:"):]
    track_data = context.chat_data.get("last_tracks", {}).get(video_id)

    if not track_data:
        await query.edit_message_text("❌ Song info not found.")
        return

    title = track_data.get("title", "Unknown Title")
    artist = track_data.get("artist", "Unknown Artist")

    filepath = get_audio_path(video_id)

    try:
        if not is_cache_valid(filepath):
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, download_audio_to_mp3, video_id)
        else:
            print(f"[CACHE] Using cached file for: {video_id}")

        with open(filepath, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                title=title,
                performer=artist,
            )
        print(f"[INFO] Song sent: {title} by {artist}")

    except Exception as e:
        print(f"[ERROR] Failed to send song: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Failed to send the song.")
