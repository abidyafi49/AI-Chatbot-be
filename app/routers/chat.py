from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.schemas import ChatRequest, Message
from app.services.gemini_services import GeminiService
from datetime import datetime

router = APIRouter(
    prefix="/chat",
    tags=["Chat Interface"]
)

ai_service = GeminiService()

@router.post("/send")
async def send_message(request: ChatRequest):
    # 1. Nanti di sini logic ambil history dari DB
    # 2. Panggil Gemini API
    # 3. Simpan ke DB
    
    try:
        bot_response = await ai_service.generate_response(request.message)
        
        return {
            "id": 1,
            "theme_id": request.theme_id or 1,
            "role" : "assistant",
            "content" : bot_response,
            "created_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))