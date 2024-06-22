from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class MessageCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    subject: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    subject: str
    status: str
    created_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class DraftReplyResponse(BaseModel):
    id: int
    conversation_id: int
    content: str
    edited_content: Optional[str] = None
    status: str
    confidence_score: int
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True


class DraftApproval(BaseModel):
    status: str  # "approved", "rejected", "edited"
    edited_content: Optional[str] = None
    reviewed_by: str
