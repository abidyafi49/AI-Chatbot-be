from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["Chat Interface"]
)

@router.post("/send")
async def send_message(theme_id: int, message: str, db: AsyncSession = Depends(get_db)):
    return {"status" : "success", "message" : f"Message accepted for theme {theme_id}"}