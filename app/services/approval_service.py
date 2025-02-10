from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Conversation, Message, DraftReply, DraftStatus, ConversationStatus
from app.services.ai_service import generate_draft_reply
from app.services.rag_service import query_knowledge_base


def create_draft_for_conversation(conversation_id: int, db: Session) -> DraftReply:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise ValueError("Gesprek niet gevonden")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    last_customer_message = ""
    conversation_history = []
    for msg in messages:
        conversation_history.append({
            "sender_type": msg.sender_type,
            "content": msg.content,
        })
        if msg.sender_type == "customer":
            last_customer_message = msg.content

    knowledge_context = query_knowledge_base(last_customer_message)

    result = generate_draft_reply(
        customer_message=last_customer_message,
        conversation_history=conversation_history,
        knowledge_context=knowledge_context,
    )

    draft = DraftReply(
        conversation_id=conversation_id,
        content=result["content"],
        confidence_score=result["confidence_score"],
        status=DraftStatus.PENDING,
    )
    db.add(draft)

    conversation.status = ConversationStatus.IN_PROGRESS
    db.commit()
    db.refresh(draft)

    return draft


def approve_draft(draft_id: int, reviewed_by: str, db: Session) -> DraftReply:
    draft = db.query(DraftReply).filter(DraftReply.id == draft_id).first()
    if not draft:
        raise ValueError("Concept antwoord niet gevonden")

    draft.status = DraftStatus.APPROVED
    draft.reviewed_at = datetime.utcnow()
    draft.reviewed_by = reviewed_by

    agent_message = Message(
        conversation_id=draft.conversation_id,
        sender_type="agent",
        content=draft.edited_content or draft.content,
    )
    db.add(agent_message)

    db.commit()
    db.refresh(draft)
    return draft


def reject_draft(draft_id: int, reviewed_by: str, db: Session) -> DraftReply:
    draft = db.query(DraftReply).filter(DraftReply.id == draft_id).first()
    if not draft:
        raise ValueError("Concept antwoord niet gevonden")

    draft.status = DraftStatus.REJECTED
    draft.reviewed_at = datetime.utcnow()
    draft.reviewed_by = reviewed_by

    db.commit()
    db.refresh(draft)
    return draft


def edit_draft(draft_id: int, edited_content: str, reviewed_by: str, db: Session) -> DraftReply:
    draft = db.query(DraftReply).filter(DraftReply.id == draft_id).first()
    if not draft:
        raise ValueError("Concept antwoord niet gevonden")

    draft.edited_content = edited_content
    draft.status = DraftStatus.EDITED
    draft.reviewed_at = datetime.utcnow()
    draft.reviewed_by = reviewed_by

    db.commit()
    db.refresh(draft)
    return draft
