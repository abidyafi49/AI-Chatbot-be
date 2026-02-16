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
            model_name="models/gemini-1.5-flash",
            system_instruction=self.system_instruction
        )
    
    async def generate_response(self, user_message: str, history: list = None):
        chat = self.model.start_chat(history=history or [])
        response = await chat.send_message_async(user_message) # non streaming
        return response.text