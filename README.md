
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Telegram%20Bot-API-success.svg" alt="Telegram Bot">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>


# 🤖 Telegram AI ChatBot with Vision Model & YouTube Music Song Downloader

This Telegram bot is a powerful AI chatbot that supports image processing (Vision Model), per-user memory, and a `/song` command to search and download music directly from YouTube Music. It can be run locally or hosted on platforms like Pterodactyl.

---

## 📦 Key Features

- ✅ **AI Chat with Vision Model Support**  
  Understands and responds to images sent by users.

- 💡 **Per-User Memory System**  
  Remembers user interactions privately, both in private chats and groups.

- 🌐 **Multi-user & Group Support**  
  Works in both private and group chats with isolated memory.

---

## 🚀 How to Run

### 1. Install Required Modules

```bash
pip install -r requirements.txt
```

### 2. Run the Bot

```bash
python3 app.py
```

### 3. Optional: Run on Pterodactyl Panel

- This bot works perfectly on the **Pterodactyl** hosting panel.
- Upload all project files.
- Use the following startup command:

```bash
python3 app.py
```

---

## 🔐 IMPORTANT: Enable `/song` to Work 100%

To make the `/song` command work reliably, you **must include cookies from YouTube.com**.

### How to Add YouTube Cookies:

1. Visit [YouTube](https://www.youtube.com) in your browser while logged in.
2. Use a browser extension like **"Get cookies.txt"**.
3. Save the exported cookies to the following location:

```
/cookies/cookies.txt
```

Make sure the file is named exactly `cookies.txt`.

❗ Without these cookies, the `/song` command may fail or return incomplete results.

---

## 🛑 When the AI Doesn't Respond

If the bot stops responding to AI chat inputs, it's likely due to a **rate limit from the provider Pollinations via g4f (free model provider)**.

✅ To fix this:

- Wait **3–5 seconds**
- Send your message again
- The bot should respond normally

---

## ⚙️ Project Structure

```
.
├── app.py                  # Main bot entry
├── aicore.py               # AI logic + vision model
├── command/
│   ├── searchsong.py       # /song command
│   ├── hello.py            # /hello command
│   ├── mymemory.py         # per-user memory access
│   └── clearmemory.py      # memory reset command
├── utils/
│   ├── dlpsendmusic.py     # YouTube downloader
│   ├── aisearchsong.py     # Song search via AI
│   └── extract_memory_ai.py# Memory parsing utils
├── cookies/
│   └── cookies.txt         # YouTube cookies file (REQUIRED)
├── requirements.txt        # Python dependencies
├── .env                    # Environment config (TOKEN, API key)
├── db.json                 # User memory store
├── dbgroup.json            # Group memory store
```

---

## 📄 Example `.env` File

Create a `.env` file in the root directory and fill it like this:

```
BOT TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_id
```


---

## 📌 Notes

- This bot supports image input (Vision AI model).
- User memory is stored privately and separately per user/group.
- Designed for both personal and group use.

---

## 🧪 Developer Notes

This project was developed by a **beginner developer** as a learning experience.  
So don't be surprised if there are bugs, missing features, or some messy code — the goal was to learn and experiment with Python, AI, and Telegram bots.

🔓 This project is also **open source**, so feel free to explore, modify, or improve it however you like.
