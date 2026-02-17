from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dto.chatDto import ChatRequestDTO, ChatResponseDTO
from app.services.chatManager import ChatManager

router = APIRouter(prefix="/chat", tags=["Chat Interface"])

@router.post("/send", response_model=ChatResponseDTO)
async def send_message(request: ChatRequestDTO, db: AsyncSession = Depends(get_db)):
    # Inisialisasi manager dengan session DB
    manager = ChatManager(db)
    
    # Jalankan proses chat
    result = await manager.process_chat(
        theme_id=request.theme_id, 
        message=request.message
    )
    
    return result # FastAPI otomatis convert Model ke DTO karena response_model