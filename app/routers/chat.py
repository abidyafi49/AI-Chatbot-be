from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dto.chatDto import ChatRequestDTO, ChatResponseDTO
from app.models.models import User
from app.services.chatManager import ChatManager
from app.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat Interface"])

@router.post("/send", response_model=ChatResponseDTO)
async def send_message(
    request: ChatRequestDTO, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Satpam beraksi di sini!
):
    # Kirim current_user ke manager agar diproses sesuai identitasnya
    manager = ChatManager(db, current_user.id)
    
    result = await manager.process_chat(
        theme_id=request.theme_id, 
        message=request.message
    )
    
    return result

@router.post("/send/stream")
async def stream_message(request: ChatRequestDTO, db: AsyncSession = Depends(get_db)):
    manager = ChatManager(db)
    
    async def event_generator():
        async for data in manager.process_streaming_chat(request.theme_id, request.message):
            # Format SSE: 'data: <content>\n\n'
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")