from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.models import User
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == user.username))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")
    
    hashed_pwd = AuthService.get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)
    db.add(new_user)
    await db.commit()
    return {"message": "User berhasil dibuat"}

@router.post("/login")
async def login(
    # Ganti UserLogin dengan OAuth2PasswordRequestForm
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    # 1. Cari user berdasarkan username dari form_data
    res = await db.execute(select(User).where(User.username == form_data.username))
    user_matched = res.scalar_one_or_none()
    
    # 2. Validasi: Cek apakah user ada DAN password cocok
    # Perbaikan logika: Kita cek user_matched, bukan variabel 'user'
    if not user_matched or not AuthService.verify_password(form_data.password, user_matched.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Username atau password salah"
        )
    
    # 3. Generate Token menggunakan username yang valid
    token = AuthService.create_access_token(data={"sub": user_matched.username})
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user