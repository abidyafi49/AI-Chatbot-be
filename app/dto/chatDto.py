from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatRequestDTO(BaseModel):
    message: str
    theme_id: Optional[int] = None

class ChatResponseDTO(BaseModel):
    id: int
    content: str
    role: str
    theme_id : int
    created_at: datetime
    
    class Config:
        from_attributes = True