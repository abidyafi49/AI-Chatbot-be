from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.models import Message as MessageModel
from app.services.gemini_services import GeminiService
from app.models.models import User, Theme
from fastapi import HTTPException
from typing import Optional
import json

class ChatManager:
    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id
        self.ai_service = GeminiService()

    async def process_chat(self, theme_id: Optional[int], message: str):
    # 1. Cari atau Buat Tema
        if not theme_id:
            current_theme = Theme(title="New Conversation", owner_id=self.user_id)
            self.db.add(current_theme)
            await self.db.commit()
            await self.db.refresh(current_theme)
        else:
            res = await self.db.execute(
                select(Theme).where(Theme.id == theme_id, Theme.owner_id == self.user_id)
            )
            current_theme = res.scalar_one_or_none()
            if not current_theme:
                raise HTTPException(status_code=403, detail="Akses ditolak")

        # 2. Simpan Pesan User ke DB
        user_msg = MessageModel(theme_id=current_theme.id, role="user", content=message)
        self.db.add(user_msg)

        # 3. Ambil Respon dari AI (Gemini)
        bot_content = await self.ai_service.generate_response(message, []) # Tambahkan history jika perlu
        bot_msg = MessageModel(theme_id=current_theme.id, role="assistant", content=bot_content)
        self.db.add(bot_msg)

        # 4. LOGIKA AUTO-SUMMARIZE & SAVE KE DB
        # Jika judul masih bawaan ("New Conversation"), kita ganti permanen
        if current_theme.title == "New Conversation":
            new_title = await self.ai_service.summarize_title(message)
            current_theme.title = new_title # Mengubah atribut objek
            
            # Beritahu DB bahwa ada perubahan pada objek current_theme
            self.db.add(current_theme) 

        # 5. COMMIT FINAL
        # Di sini SQL akan menjalankan INSERT untuk 2 pesan dan UPDATE untuk 1 judul tema
        await self.db.commit()
        await self.db.refresh(bot_msg)

        # 6. RETURN DATA RATAL (Agar tidak Error 500 lagi)
        return {
            "id": bot_msg.id,
            "role": bot_msg.role,
            "content": bot_msg.content,
            "created_at": bot_msg.created_at,
            "theme_id": current_theme.id,
            "theme_title": current_theme.title # Frontend akan menerima judul baru di sini
        }
    
    async def process_streaming_chat(self, theme_id: Optional[int], message: str):
        # 1. Handle Theme & User Message (sama seperti sebelumnya)
        if not theme_id:
            current_theme = Theme(title="New Conversation")
            self.db.add(current_theme)
            await self.db.commit()
            await self.db.refresh(current_theme)
        else:
            res = await self.db.execute(select(Theme).where(Theme.id == theme_id))
            current_theme = res.scalar_one_or_none()

        # Simpan pesan user dulu
        user_msg = MessageModel(theme_id=current_theme.id, role="user", content=message)
        self.db.add(user_msg)
        await self.db.commit()

        # 2. Ambil History
        res_history = await self.db.execute(
            select(MessageModel).where(MessageModel.theme_id == current_theme.id)
            .order_by(MessageModel.created_at.asc()).limit(10)
        )
        history = res_history.scalars().all()

        # 3. Stream Generator
        full_ai_content = ""
        async for chunk in self.ai_service.generate_streaming_response(message, history):
            full_ai_content += chunk
            # Kirim dalam format JSON agar mudah dibaca Frontend
            yield json.dumps({"chunk": chunk, "theme_id": current_theme.id})

        # 4. Finalisasi: Simpan jawaban lengkap AI ke DB
        bot_msg = MessageModel(theme_id=current_theme.id, role="assistant", content=full_ai_content)
        self.db.add(bot_msg)

        # 5. Auto-Summarize jika perlu
        if current_theme.title == "New Conversation":
            current_theme.title = await self.ai_service.summarize_title(message)

        await self.db.commit()
        
    async def get_theme_details(self, theme_id: int):
        # Cari tema, tapi filter hanya yang owner_id-nya sesuai user yang login
        result = await self.db.execute(
            select(Theme)
            .options(selectinload(Theme.messages)) # Ambil pesan-pesannya sekalian
            .where(Theme.id == theme_id, Theme.owner_id == self.user_id)
        )
        theme = result.scalar_one_or_none()
        
        if not theme:
            # Jika ID ada tapi punya orang lain, kita bilang 'Not Found' demi keamanan
            raise HTTPException(status_code=404, detail="Tema tidak ditemukan atau akses ditolak")
            
        return theme