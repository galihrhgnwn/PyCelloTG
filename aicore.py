# aicore.py

import g4f
import g4f.Provider
from typing import List, Dict
from PIL import Image

class AICore:
    def __init__(self):
        # Provider vision-compatible
        self.client = g4f.Client(provider=g4f.Provider.LMArenaBeta)

    def _build_messages(self, history: List[Dict], prompt: str, is_image: bool = False) -> List[Dict]:
        system_content = (
            "You are a helpful assistant. When analyzing images, give clear and concise descriptions. "
            "Avoid using Markdown (like **bold**, _italic_, or `code`). "
            "Keep your answers clean and easy to read. "
            "Match the user's language and tone — use casual or slang if the user does, but stay appropriate."
            if is_image else
            "You are a helpful assistant. Answer clearly and directly. "
            "Avoid using Markdown (like **bold**, _italic_, or `code`). "
            "Keep your answers clean and easy to read. "
            "Match the user's language and tone — use casual or slang if the user does, but stay appropriate."
        )

        system_prompt = {"role": "system", "content": system_content}
        return [system_prompt] + history + [{"role": "user", "content": prompt}]

    def chat(self, prompt: str, history: List[Dict] = None) -> str:
        if history is None:
            history = []

        messages = self._build_messages(history, prompt)
        response = self.client.chat.completions.create(
            messages=messages,
            model="claude-sonnet-4-20250514"  # change to another model if necessary
        )
        return response.choices[0].message.content.strip()

    def chat_with_image(self, prompt: str, image_path: str, history: List[Dict] = None) -> str:
        if history is None:
            history = []

        with open(image_path, "rb") as image_file:
            images = [[image_file, image_path]]
            messages = self._build_messages(history, prompt, is_image=True)
            response = self.client.chat.completions.create(
                messages=messages,
                model="claude-sonnet-4-20250514",  # change to another model if necessary
                images=images
            )
            return response.choices[0].message.content.strip()
