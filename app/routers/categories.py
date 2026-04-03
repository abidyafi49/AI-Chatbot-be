from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.models import User
from app.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import User, Category

router = APIRouter(prefix="/chat", tags=["Chat Interface"])


@router.get("/folders")
async def get_folders_with_themes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ambil semua kategori milik user beserta tema di dalamnya
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.themes))
        .where(Category.owner_id == current_user.id)
    )
    return result.scalars().all()