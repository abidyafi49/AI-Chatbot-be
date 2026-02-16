from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.schemas import ChatRequest, Message

router = APIRouter(
    prefix="/chat",
    tags=["Chat Interface"]
)

@router.post("/send")
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Nanti di sini logic ambil history dari DB
    # 2. Panggil Gemini API
    # 3. Simpan ke DB
    
    return {
        "id": 1,
        "theme_id": request.theme_id or 99,
        "role": "assistant",
        "content": f"kamu tadi tanya: {request.message}. tunggu ya ai lagi nyiapin",
        "created_at": "2026-02-16T00:00:00"
    }