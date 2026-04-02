from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.models import Theme, User
from app.schemas.schemas import Theme as ThemeSchema
from app.dto.chatDto import ThemeDetailDTO, ThemeCreateDTO, ThemeResponseDTO
from app.services.chatManager import ChatManager
from typing import List

router = APIRouter(prefix="/themes", tags=["Theme Management"])

@router.get("/", response_model=List[ThemeResponseDTO])
async def get_my_themes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Satpam beraksi!
):
    # FILTER: Hanya ambil tema yang owner_id-nya adalah ID user yang sedang login
    result = await db.execute(
        select(Theme)
        .where(Theme.owner_id == current_user.id)
        .order_by(Theme.created_at.desc()) # Urutkan dari yang terbaru
    )
    themes = result.scalars().all()
    
    return themes

@router.post("/", response_model=ThemeResponseDTO)
async def create_new_theme(
    theme_input: ThemeCreateDTO,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Cek siapa yang buat
):
    # 1. Buat objek tema baru dan hubungkan ke ID user yang sedang login
    new_theme = Theme(
        title=theme_input.title,
        owner_id=current_user.id
    )
    
    # 2. Simpan ke Database
    db.add(new_theme)
    await db.commit()
    await db.refresh(new_theme)
    
    # 3. Kembalikan data tema yang sudah ada ID-nya dari DB
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
    # Panggil manager dengan user_id yang didapat dari token
    manager = ChatManager(db, current_user.id)
    
    # Ambil data
    theme_data = await manager.get_theme_details(theme_id)
    
    return theme_data