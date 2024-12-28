"""Script to import historical customer support conversations for learning."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import Conversation, Message, KnowledgeDocument, ConversationStatus
from app.services.rag_service import add_document


def import_from_json(file_path: str):
    """Import historical conversations from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    init_db()

    imported = 0
    for conv_data in data.get("conversations", []):
        conversation = Conversation(
            customer_name=conv_data["customer_name"],
            customer_email=conv_data.get("customer_email", "historisch@voorbeeld.nl"),
            subject=conv_data["subject"],
            status=ConversationStatus.CLOSED,
        )
        db.add(conversation)
        db.flush()

        for msg_data in conv_data.get("messages", []):
            message = Message(
                conversation_id=conversation.id,
                sender_type=msg_data["sender_type"],
                content=msg_data["content"],
            )
            db.add(message)

        full_conversation = "\n\n".join(
            f"{'Klant' if m['sender_type'] == 'customer' else 'Medewerker'}: {m['content']}"
            for m in conv_data.get("messages", [])
        )
        add_document(
            doc_id=f"history_{conversation.id}",
            content=full_conversation,
            metadata={
                "source": "Historisch gesprek",
                "doc_type": "historical",
                "subject": conv_data["subject"],
            },
        )

        imported += 1

    db.commit()
    db.close()

    print(f"Geïmporteerd: {imported} historische gesprekken")
    return imported


def import_resolved_conversations():
    """Import resolved conversations from the database into the knowledge base."""
    db = SessionLocal()

    conversations = db.query(Conversation).filter(
        Conversation.status.in_([ConversationStatus.RESOLVED, ConversationStatus.CLOSED])
    ).all()

    added = 0
    for conv in conversations:
        if len(conv.messages) < 2:
            continue

        full_conversation = "\n\n".join(
            f"{'Klant' if m.sender_type == 'customer' else 'Medewerker'}: {m.content}"
            for m in conv.messages
        )

        add_document(
            doc_id=f"resolved_{conv.id}",
            content=full_conversation,
            metadata={
                "source": "Opgelost gesprek",
                "doc_type": "historical",
                "subject": conv.subject,
            },
        )
        added += 1

    db.close()
    print(f"Toegevoegd aan kennisbank: {added} opgeloste gesprekken")
    return added


if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_from_json(sys.argv[1])
    else:
        print("Gebruik: python scripts/import_history.py <bestand.json>")
        print("Of importeer opgeloste gesprekken uit de database:")
        import_resolved_conversations()
