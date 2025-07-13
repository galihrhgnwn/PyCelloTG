# command/generateimage.py

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from telegram.ext import ContextTypes, CallbackQueryHandler
from g4f.client import Client
import g4f
import io, requests, asyncio, uuid
import json

command = "generateimage"
_CB_PREFIX = "genimg"
_callback_registered = False
_prompt_cache: dict[str, str] = {}

def _cache_prompt(prompt: str) -> str:
    prompt_id = uuid.uuid4().hex[:12]
    _prompt_cache[prompt_id] = prompt
    return prompt_id

def _get_prompt(prompt_id: str) -> str | None:
    return _prompt_cache.get(prompt_id)

async def _extract_dimensions(prompt: str) -> tuple[int, int]:
    client = g4f.Client(provider=g4f.Provider.Blackbox)
    messages = [
        {"role": "system", "content": "You are an assistant that helps decide ideal image dimensions."},
        {"role": "user", "content": f"For this prompt: '{prompt}', give ideal image width and height (in pixels) to generate a high-quality image. Answer only in JSON like: {{\"width\":1024,\"height\":768}}."}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=False
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        width = int(data.get("width", 512))
        height = int(data.get("height", 512))
        return width, height
    except Exception as e:
        print(f"[extract_dimensions] fallback to 512x512: {e}")
        return 512, 512

async def _generate_image_bytes(prompt: str, width: int, height: int) -> io.BytesIO | None:
    loop = asyncio.get_running_loop()
    client = Client()

    def _run():
        return client.images.generate(
            model="flux",
            prompt=prompt,
            response_format="url",
            provider=g4f.Provider.PollinationsImage,
            width=width,
            height=height,
            enhance=True,
            seed=uuid.uuid4().int % 100000  # randomize output
        )

    response = await loop.run_in_executor(None, _run)

    if not response or not getattr(response, "data", None):
        return None

    url = response.data[0].url
    img_bytes = requests.get(url).content
    stream = io.BytesIO(img_bytes)
    stream.name = "generated.png"
    return stream

def _keyboard(prompt: str) -> InlineKeyboardMarkup:
    prompt_id = _cache_prompt(prompt)
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 More", callback_data=f"{_CB_PREFIX}|{prompt_id}")]]
    )

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _callback_registered

    if update.effective_chat.type != "private":
        await update.message.reply_text("❌ This command can only be used in private chat.")
        return

    prompt = " ".join(context.args).strip()
    if not prompt:
        await update.message.reply_text(
            "📸 Please provide an image prompt.\n"
            "Example: /generateimage a hyperrealistic lion in the jungle"
        )
        return

    loading = await update.message.reply_text("🎨 Generating image, please wait...")

    width, height = await _extract_dimensions(prompt)
    image = await _generate_image_bytes(prompt, width, height)

    if image:
        await update.message.reply_photo(
            photo=image,
            caption=f"🖼️ Prompt: {prompt}\nSize: {width}x{height}",
            reply_markup=_keyboard(prompt),
        )
    else:
        await update.message.reply_text("❌ Failed to generate image. No result was returned.")

    await loading.delete()

    if not _callback_registered:
        context.application.add_handler(
            CallbackQueryHandler(_more_callback, pattern=f"^{_CB_PREFIX}\\|")
        )
        _callback_registered = True

async def _more_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query: CallbackQuery = update.callback_query
    await query.answer("🎨 Generating image, please wait...", show_alert=False)

    _, prompt_id = query.data.split("|", 1)
    prompt = _get_prompt(prompt_id)

    if not prompt:
        await query.message.reply_text("⚠️ Prompt not found (expired). Please run /generateimage again.")
        return

    width, height = await _extract_dimensions(prompt)
    image = await _generate_image_bytes(prompt, width, height)

    if image:
        await query.message.reply_photo(
            photo=image,
            caption=f"🖼️ Prompt: {prompt}\nSize: {width}x{height}",
            reply_markup=_keyboard(prompt),
        )
    else:
        await query.message.reply_text("❌ Failed to generate image.")
