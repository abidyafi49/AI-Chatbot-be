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
    
    async def summarize_title(self, first_message: str):
        # Buat prompt yang sangat ketat
        prompt = f"""
        Tugas: Berikan SATU judul singkat (maksimal 5 kata) untuk percakapan yang diawali dengan pesan: "{first_message}"
        Aturan:
        1. JANGAN berikan pilihan.
        2. JANGAN pakai tanda kutip.
        3. LANGSUNG berikan judulnya saja.
        4. Gunakan Bahasa sesuai dengan yang digunakan chat.
        """
        
        # Panggil model Gemini
        response = self.model.generate_content(prompt)
        
        # Bersihkan hasilnya (hapus spasi atau baris baru yang nggak perlu)
        title = response.text.strip()
        
        if "\n" in title:
            title = title.split("\n")[0].replace("*", "").strip()
            
        return title
    
    async def generate_streaming_response(self, user_message: str, history: list = None):
        formatted_history = []
        if history:
            for msg in history:
                role = "model" if msg.role == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [msg.content]})
        
        chat = self.model.start_chat(history=formatted_history)
        
        response = await chat.send_message_async(user_message, stream=True)
        
        async for chunk in response:
            if chunk.text:
                yield chunk.text
                
    async def get_simple_category(self, text: str):
        prompt = f"""
        Tugas: Kategorikan percakapan ini ke dalam SATU topik besar.
        Pilihan utama: Pemrograman, Bisnis, Kesehatan, Pendidikan, Hiburan.
        Jika tidak masuk kategori di atas, buat kategori baru maksimal 1 kata.
        
        Isi Percakapan: "{text}"
        
        Balas HANYA dengan nama kategorinya saja.
        """
        response = await self.model.generate_content(prompt)
        return response.text.strip()