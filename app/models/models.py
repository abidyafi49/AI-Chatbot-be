from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relasi ke Tema
    themes = relationship("Theme", back_populates="owner")
    categories = relationship("Category", back_populates="owner")

class Theme(Base):
    __tablename__ = "themes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True) # KUNCI UTAMA: Milik siapa?
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="themes")
    messages = relationship("Message", back_populates="theme", cascade="all, delete-orphan")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="themes")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), index=True)
    role = Column(String) # 'user' atau 'assistant'
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    theme = relationship("Theme", back_populates="messages")
    
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Relasi
    owner = relationship("User", back_populates="categories")
    themes = relationship("Theme", back_populates="category")