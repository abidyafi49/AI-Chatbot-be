from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, Date
from app.db.database import get_db
from app.models.models import Message
from app.models.models import Theme
from datetime import datetime, date
from app.core.config import ADMIN_KEY


async def verify_admin_token(x_admin_token: str = Header(...)):
    if x_admin_token != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access only")

router = APIRouter(
    prefix="/admin",
    tags=["Admin Only"],
    dependencies=[Depends(verify_admin_token)],
    responses={404: {"description": "Not found"}}
)

@router.get("/stats")
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    # 1. Hitung Total Tema
    theme_count_res = await db.execute(select(func.count(Theme.id)))
    total_themes = theme_count_res.scalar()

    # 2. Hitung Total Pesan
    msg_count_res = await db.execute(select(func.count(Message.id)))
    total_messages = msg_count_res.scalar()

    # 3. Hitung Tema Baru Hari Ini
    today = date.today()
    new_themes_today_res = await db.execute(
        select(func.count(Theme.id)).where(func.cast(Theme.created_at, Date) == today)
    )
    new_themes_today = new_themes_today_res.scalar()

    return {
        "summary": {
            "total_themes": total_themes,
            "total_messages": total_messages,
            "new_themes_today": new_themes_today
        },
        "server_status": "online",
        "timestamp": datetime.now()
    }
    
@router.get("/recent-themes")
async def get_recent_themes(limit: int = 5, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Theme).order_by(Theme.created_at.desc()).limit(limit)
    )
    themes = result.scalars().all()
    return themes