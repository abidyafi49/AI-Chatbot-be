from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    role: str
    content: str
    
class MessageCreate(MessageBase):
    theme_id: int
    
class Message(MessageBase):
    id: int
    theme_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
class ThemeBase(BaseModel):
    title: str

class ThemeCreate(ThemeBase):
    pass

class Theme(ThemeBase):
    id: int
    created_at: datetime
    messages: List[Message] = []
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    theme_id: Optional[int] = None