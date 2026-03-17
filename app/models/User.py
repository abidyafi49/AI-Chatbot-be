from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Relasi ke Tema
    themes = relationship("Theme", back_populates="owner")

class Theme(Base):
    __tablename__ = "themes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id")) # Link ke User
    
    owner = relationship("User", back_populates="themes")
    messages = relationship("Message", back_populates="theme")