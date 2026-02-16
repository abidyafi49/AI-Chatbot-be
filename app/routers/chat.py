from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.schemas.schemas import ChatRequest, Message
from app.models.models import Message as MessageModel, Theme
from app.services.gemini_services import GeminiService
from datetime import datetime

router = APIRouter(
    prefix="/chat",
    tags=["Chat Interface"]
)
ai_service = GeminiService()

@router.post("/send")
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not request.theme_id:
        new_theme = Theme(title= "New Conversation")
        db.add(new_theme)
        await db.commit()
        await db.refresh()
        theme_id = new_theme.id
    else:
        theme_id = request.theme_id
        
    result = await db.execute(
        select(MessageModel)
        .where(MessageModel.theme_id == theme_id)
        .order_by(MessageModel.created_at.asc())
        .limit(10)
    )
    
    history = result.scalars().all()
    
    user_msg = MessageModel(theme_id = theme_id, role = "user", content = request.message)
    db.add(user_msg)
    
    bot_content = await ai_service.generate_response(request.message, history)
    bot_msg = MessageModel(theme_id=theme_id, role="assistant", content=bot_content)
    db.add(bot_msg)
    
    await db.commit()
    await db.refresh(bot_msg)

    return bot_msg