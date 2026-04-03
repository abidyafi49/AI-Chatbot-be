from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatRequestDTO(BaseModel):
    message: str
    theme_id: Optional[int] = None

class ChatResponseDTO(BaseModel):
    id: int
    content: str
    role: str
    theme_id : int
    created_at: datetime
    
    # Tambahkan field extra untuk info tema
    theme_id: int
    theme_title: str
    
    class Config:
        from_attributes = True
        
class MessageDTO(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ThemeDetailDTO(BaseModel):
    id: int
    title: str
    messages: List[MessageDTO]
    
# Data yang dikirim dari Frontend
class ThemeCreateDTO(BaseModel):
    title: str = "Percakapan Baru"

# Data yang kita balas ke Frontend
class ThemeResponseDTO(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True
        
class CategoryDTO(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True