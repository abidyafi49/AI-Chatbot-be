from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.models.models import Theme
from app.schemas.schemas import Theme as ThemeSchema
from typing import List

router = APIRouter(prefix="/themes", tags=["Theme Management"])

@router.get("/", response_model=List[ThemeSchema])
async def get_all_themes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Theme)
        .options(selectinload(Theme.messages))
        .order_by(Theme.created_at.desc())
    )
    return result.scalars().all()

@router.delete("/{theme_id}")
async def delete_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="Tema tidak ditemukan")
    
    await db.delete(theme)
    await db.commit()
    return {"message": f"Tema {theme_id} berhasil dihapus"}