from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.models import User
from app.core.config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, # Gunakan 'Bearer' (B kapital) sesuai standar
    )
    try:
        # 1. Debug: Cek apakah token masuk ke fungsi
        print(f"DEBUG: Menerima token: {token}") 
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        
        print(f"DEBUG: Username dari token: {username}")
        
        if username is None:
            raise credentials_exception
            
    except JWTError as e: # FIX: Tambahkan 'as e' di sini
        print(f"DEBUG: JWT Error Terdeteksi: {str(e)}") 
        raise credentials_exception

    # 2. Cari user di DB
    res = await db.execute(select(User).where(User.username == username))
    user = res.scalar_one_or_none()
    
    if user is None:
        print(f"DEBUG: User {username} tidak ada di database")
        raise credentials_exception
        
    return user