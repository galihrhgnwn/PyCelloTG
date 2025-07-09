# utils/aisearchsong.py

import g4f

PROVIDER = g4f.Provider.Blackbox
MODEL = "gpt-4o"

async def generate_ai_slang(title: str, artist_names: str, time: float) -> str:
    prompt = (
    f"Explain the meaning of the song '{title}' by {artist_names}' "
    "in just one creative sentence using casual American slang, abbreviations, and expressions (like tbh, ngl, fr, etc). "
    "Do NOT say things like 'hits hard' or 'gives the feels'. Avoid repeating phrases. Be original, fun, and brief."
)

    try:
        response = g4f.ChatCompletion.create(
            model=MODEL,
            provider=PROVIDER,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        if isinstance(response, str):
            return response.strip()
        else:
            return str(response)
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return f"✅ Found <i>{title}</i> in {time:.2f}s 😎"  # fallback