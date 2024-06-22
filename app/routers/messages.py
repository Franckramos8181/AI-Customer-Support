from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Message, ConversationStatus
from app.schemas import MessageCreate, ConversationResponse, ConversationListItem

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/", response_model=ConversationResponse)
async def receive_message(message: MessageCreate, db: Session = Depends(get_db)):
    conversation = Conversation(
        customer_name=message.customer_name,
        customer_email=message.customer_email,
        subject=message.subject,
        status=ConversationStatus.OPEN,
    )
    db.add(conversation)
    db.flush()

    msg = Message(
        conversation_id=conversation.id,
        sender_type="customer",
        content=message.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.post("/{conversation_id}/reply")
async def add_customer_reply(conversation_id: int, content: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Gesprek niet gevonden")

    msg = Message(
        conversation_id=conversation_id,
        sender_type="customer",
        content=content,
    )
    db.add(msg)
    db.commit()

    return {"status": "received", "conversation_id": conversation_id}


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(Conversation)
    if status:
        query = query.filter(Conversation.status == status)
    conversations = query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    result = []
    for conv in conversations:
        item = ConversationListItem(
            id=conv.id,
            customer_name=conv.customer_name,
            customer_email=conv.customer_email,
            subject=conv.subject,
            status=conv.status,
            created_at=conv.created_at,
            message_count=len(conv.messages),
        )
        result.append(item)
    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Gesprek niet gevonden")
    return conversation
