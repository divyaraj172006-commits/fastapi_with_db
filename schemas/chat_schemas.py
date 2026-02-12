from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    created_at: datetime
    is_pinned: bool
    messages: List[ChatMessageResponse] = []
    
    class Config:
        orm_mode = True
