# utils/extract_memory_ai.py

import g4f

PROVIDER = g4f.Provider.DeepInfra
MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct"

def extract_memory_from_message(message: str) -> dict:
    prompt = f"""
You are a long-term memory system for a Telegram bot.

Your task is to read one user message and extract all personal or meaningful information that could help the AI understand the user better in the future.

This includes (but is not limited to):
- Name, location, hobbies, job, favorite food/drinks
- Personality traits, habits, fears, trauma, aspirations
- Personal stories, life experiences, emotions shared
- Anything important that could be part of the user's identity

Output must be in pure JSON format.
JSON keys are flexible and should adapt to the content of the message.
Values can be full sentences if needed.

If there is no meaningful info, respond with: {{}}

Do not include any explanations, only return JSON.

User message:
\"{message}\"
"""

    try:
        response = g4f.ChatCompletion.create(
            model=MODEL,
            provider=PROVIDER,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        content = response.strip()
        return eval(content) if content.startswith("{") else {}
    except Exception as e:
        print("Failed to extract memory:", e)
        return {}
