import os
from google import generativeai
from dotenv import load_dotenv

load_dotenv()

generativeai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        # Instruksi sistem agar AI konsisten dengan temanya
        self.system_instruction = (
            "Kamu adalah 'StudyBuddy', asisten belajar yang suportif dan cerdas. "
            "Tugasmu adalah membantu pengguna memahami konsep sulit dengan penjelasan sederhana. "
            "Gunakan format Markdown untuk menjelaskan sesuatu (bold, list, atau code block jika perlu)."
        )
        
        self.model = generativeai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            system_instruction=self.system_instruction
        )
    
    async def generate_response(self, user_message: str, history: list = None):
        formatted_history = []
        if history:
            for msg in history:
                role = "model" if msg.role == "assistant" else "user"
                formatted_history.append({"role" : role, "parts": [msg.content]})
                
        chat = self.model.start_chat(history=formatted_history)
        response = await chat.send_message_async(user_message) # non streaming
        return response.text
    
    async def summarize_title(self, first_message: str) -> str:
        prompt = (
            f"Buatkan judul singkat maksimal 5 kata dalam bahasa indonesia "
            f"yang merangkum pesan berikut untuk sebuah chat: '{first_message}'"
        )
        
        response  = await self.model.generate_content_async(prompt)
        title = response.text.strip().replace('"','').replace('.','')
        return title