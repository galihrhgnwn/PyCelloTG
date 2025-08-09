# aicore.py (New Version)

import requests
from typing import List, Dict

class AICore:
    def __init__(self):
        """
        Initializes the AI Core with the configuration for your personal API.
        """
        self.api_url = "http://34.230.14.150:1337/api/DeepInfra/chat/completions"
        self.model_name = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
        self.headers = {"Content-Type": "application/json"}

    def _build_messages(self, history: List[Dict], prompt: str) -> List[Dict]:
        """
        Builds the list of messages to be sent to the API, including the new system prompt.
        """
        # Your new, detailed system prompt is placed here.
        system_content = (
            "Anda adalah asisten AI yang cerdas dan teknis. Tugas Anda adalah menjawab pertanyaan dengan "
            "jelas, rapi, dan ringkas, seperti seorang ilmuwan. Gunakan bahasa yang mudah dipahami dan "
            "sesuaikan dengan gaya pengetikan pengguna. Sertakan slang yang relevan jika diperlukan untuk "
            "menjaga suasana tetap friendly dan asik. Pastikan setiap jawaban informatif dan menunjukkan "
            "tingkat kepintaran yang tinggi. Jangan bertele-tele dan langsung ke inti permasalahan. "
            "Selalu ikuti gaya dan nada yang digunakan"
            "oleh pengguna dalam input mereka."
        )

        system_prompt = {"role": "system", "content": system_content}
        
        if history is None:
            history = []
            
        return [system_prompt] + history + [{"role": "user", "content": prompt}]

    def chat(self, prompt: str, history: List[Dict] = None) -> str:
        """
        Sends a text prompt to the personal API and returns the response.
        """
        messages = self._build_messages(history, prompt)

        payload = {
            "provider": "DeepInfra",
            "model": self.model_name,
            "messages": messages,
            "web_search": True,
            "temperature": 0.8,
            "max_tokens": 1500
        }

        try:
            # Send the request to your API
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_data = response.json()
                # This is the key part: extracting the answer text from the JSON structure
                return response_data['choices'][0]['message']['content'].strip()
            else:
                # Handle server-side errors (e.g., 404, 500)
                error_info = f"API Error: Status {response.status_code} - {response.text}"
                print(error_info)
                return "Maaf, terjadi kesalahan internal pada layanan AI."

        except requests.exceptions.RequestException as e:
            # Handle connection errors (e.g., timeout, server unreachable)
            print(f"Connection Error: {e}")
            return "Maaf, gagal terhubung ke layanan AI. Mohon coba lagi nanti."

    def chat_with_image(self, prompt: str, image_path: str, history: List[Dict] = None) -> str:
        """
        Image functionality is currently disabled because the personal API
        does not yet support image file submissions.
        """
        print("Warning: chat_with_image function was called, but it is not supported by the current API.")
        
        # Return a clear error message to the bot's user.
        return "Maaf, fungsionalitas untuk menganalisis gambar belum didukung saat ini."
        
        # --- NOTE FOR FUTURE DEVELOPMENT ---
        # If you want to add image support to your API, you will need to:
        # 1. Modify your API backend (at 34.230.14.150) to accept image data.
        #    A common method is via 'multipart/form-data' or accepting a base64 encoded string.
        # 2. If you choose base64, you can modify the currently disabled code below.
        #
        # import base64
        #
        # with open(image_path, "rb") as image_file:
        #     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        #
        # # The _build_messages function would need to be called with is_image=True
        # messages = self._build_messages(history, prompt) # You might need to adapt this part
        #
        # # Your payload MUST be modified to include the image data
        # payload = {
        #     "model": self.model_name,
        #     "messages": messages,
        #     "images": [base64_image] # This is JUST AN EXAMPLE, the actual format depends on your API
        # }
        # # Then, continue with the request...
