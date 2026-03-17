from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.models import User
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Cek apakah user sudah ada
    res = await db.execute(select(User).where(User.username == username))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")
    
    hashed_pwd = AuthService.get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_pwd)
    db.add(new_user)
    await db.commit()
    return {"message": "User berhasil dibuat"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == form_data.username))
    user = res.scalar_one_or_none()
    
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}