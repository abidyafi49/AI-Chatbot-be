from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import Theme, User
from app.schemas.schemas import Theme as ThemeSchema
from app.dto.chatDto import ThemeDetailDTO, ThemeCreateDTO, ThemeResponseDTO
from app.services.chatManager import ChatManager
from typing import List

router = APIRouter(prefix="/themes", tags=["Theme Management"])

@router.post("/", response_model=ThemeResponseDTO)
async def create_new_theme(
    theme_input: ThemeCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_theme = Theme(
        title=theme_input.title,
        owner_id=current_user.id
    )
    
    db.add(new_theme)
    await db.commit()
    await db.refresh(new_theme)
    
    return new_theme

@router.delete("/{theme_id}")
async def delete_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="Tema tidak ditemukan")
    
    await db.delete(theme)
    await db.commit()
    return {"message": f"Tema {theme_id} berhasil dihapus"}

@router.get("/{theme_id}", response_model=ThemeDetailDTO)
async def get_specific_theme(
    theme_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    manager = ChatManager(db, current_user.id)
    theme_data = await manager.get_theme_details(theme_id)
    
    return theme_data

@router.post("/{theme_id}/categorize")
async def manual_categorize(
    theme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    manager = ChatManager(db, current_user.id)
    category_name = await manager.auto_categorize_theme(theme_id)
    
    if not category_name:
        raise HTTPException(status_code=400, detail="Gagal mengategorikan tema ini")
        
    return {
        "message": "Tema berhasil dikategorikan",
        "category": category_name,
        "theme_id": theme_id
    }
    
@router.get("/", response_model=list[ThemeResponseDTO])
async def get_themes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(Theme)
            .options(joinedload(Theme.category))
            .where(Theme.owner_id == current_user.id)
            .order_by(Theme.created_at.desc())
        )
        themes = result.scalars().all()

        for theme in themes:
            if theme.category:
                theme.category_name = theme.category.name
            else:
                theme.category_name = "Uncategorized"
                
        return themes
    except Exception as e:
        print(f"Error Detail: {e}") 
        raise HTTPException(status_code=500, detail=str(e))