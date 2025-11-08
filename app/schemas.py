from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema voor het aanmaken van een nieuw klantbericht."""
    customer_name: str = Field(..., min_length=1, max_length=255, description="Naam van de klant")
    customer_email: str = Field(..., min_length=5, max_length=255, description="E-mailadres van de klant")
    subject: str = Field(..., min_length=1, max_length=500, description="Onderwerp van het bericht")
    content: str = Field(..., min_length=1, description="Inhoud van het klantbericht")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Jan de Vries",
                "customer_email": "jan@voorbeeld.nl",
                "subject": "Vraag over mijn bestelling",
                "content": "Goedemiddag, ik heb een vraag over mijn bestelling #12345...",
            }
        }


class MessageResponse(BaseModel):
    """Antwoordschema voor een enkel bericht."""
    id: int
    conversation_id: int
    sender_type: str = Field(..., description="Type afzender: 'customer' of 'agent'")
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Volledig gespreksoverzicht met alle berichten."""
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
    """Verkort gespreksoverzicht voor lijstweergave."""
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
    """Antwoordschema voor een AI-gegenereerd concept antwoord."""
    id: int
    conversation_id: int
    content: str = Field(..., description="AI-gegenereerde inhoud")
    edited_content: Optional[str] = Field(None, description="Door medewerker bewerkte inhoud")
    status: str = Field(..., description="Status: pending, approved, rejected, edited")
    confidence_score: int = Field(..., ge=0, le=100, description="Vertrouwensscore (0-100)")
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True


class DraftApproval(BaseModel):
    """Schema voor het beoordelen van een concept antwoord."""
    status: str = Field(..., description="Beoordeling: 'approved', 'rejected', of 'edited'")
    edited_content: Optional[str] = Field(None, description="Bewerkte inhoud (vereist bij status 'edited')")
    reviewed_by: str = Field(..., description="Naam van de beoordelaar")


class ErrorResponse(BaseModel):
    """Standaard foutmelding."""
    detail: str = Field(..., description="Beschrijving van de fout")
    status_code: int = Field(..., description="HTTP statuscode")


class HealthResponse(BaseModel):
    """Antwoordschema voor de health check."""
    status: str
    service: str


class StatusResponse(BaseModel):
    """Antwoordschema voor de API status."""
    status: str
    version: str
    service: str


class KnowledgeDocumentResponse(BaseModel):
    """Antwoordschema voor een kennisbank document."""
    id: int
    title: str
    source: str
    doc_type: str
    created_at: datetime


class KnowledgeSearchResponse(BaseModel):
    """Antwoordschema voor een kennisbank zoekopdracht."""
    query: str
    context: str
