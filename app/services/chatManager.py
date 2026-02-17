from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Message as MessageModel, Theme
from app.services.gemini_services import GeminiService
from fastapi import HTTPException
from typing import Optional

class ChatManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = GeminiService()

    async def process_chat(self, theme_id: Optional[int], message: str):
        # 1. Handle Theme
        if not theme_id:
            current_theme = Theme(title="New Conversation")
            self.db.add(current_theme)
            await self.db.commit()
            await self.db.refresh(current_theme)
        else:
            res = await self.db.execute(select(Theme).where(Theme.id == theme_id))
            current_theme = res.scalar_one_or_none()
            if not current_theme:
                raise HTTPException(status_code=404, detail="Theme not found")

        # 2. Get History
        res_history = await self.db.execute(
            select(MessageModel)
            .where(MessageModel.theme_id == current_theme.id)
            .order_by(MessageModel.created_at.asc()).limit(10)
        )
        history = res_history.scalars().all()

        # 3. Save User Message
        user_msg = MessageModel(theme_id=current_theme.id, role="user", content=message)
        self.db.add(user_msg)

        # 4. Get AI Response
        bot_content = await self.ai_service.generate_response(message, history)
        bot_msg = MessageModel(theme_id=current_theme.id, role="assistant", content=bot_content)
        self.db.add(bot_msg)

        # 5. Auto-Summarize
        if current_theme.title == "New Conversation":
            current_theme.title = await self.ai_service.summarize_title(message)

        await self.db.commit()
        await self.db.refresh(bot_msg)
        return bot_msg