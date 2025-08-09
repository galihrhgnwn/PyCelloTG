# utils/aisearchsong.py

import g4f

PROVIDER = g4f.Provider.DeepInfra
MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct"

async def generate_ai_slang(title: str, artist_names: str, time: float) -> str:
    prompt = (
        f"Explain the meaning of the song '{title}' by {artist_names} "
        "in one concise and creative sentence in American English, "
        "and include relevant emojis that match the song's meaning."
    )

    try:
        response = g4f.ChatCompletion.create(
            model=MODEL,
            provider=PROVIDER,
            messages=[{"role": "user", "content": prompt}],
            web_search=True,  # aktifin web search
            stream=False
        )

        if isinstance(response, str):
            return response.strip()
        else:
            return str(response)
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return f"✅ Found <i>{title}</i> in {time:.2f}s 😎"  # fallback
