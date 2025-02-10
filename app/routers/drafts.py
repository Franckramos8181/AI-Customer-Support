from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DraftReply
from app.schemas import DraftReplyResponse, DraftApproval
from app.services.approval_service import (
    create_draft_for_conversation,
    approve_draft,
    reject_draft,
    edit_draft,
)

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


@router.post("/generate/{conversation_id}", response_model=DraftReplyResponse)
async def generate_draft(conversation_id: int, db: Session = Depends(get_db)):
    try:
        draft = create_draft_for_conversation(conversation_id, db)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fout bij genereren: {str(e)}")


@router.get("/{conversation_id}", response_model=list[DraftReplyResponse])
async def get_drafts(conversation_id: int, db: Session = Depends(get_db)):
    drafts = db.query(DraftReply).filter(
        DraftReply.conversation_id == conversation_id
    ).order_by(DraftReply.created_at.desc()).all()
    return drafts


@router.post("/{draft_id}/approve", response_model=DraftReplyResponse)
async def approve(draft_id: int, reviewed_by: str = "agent", db: Session = Depends(get_db)):
    try:
        draft = approve_draft(draft_id, reviewed_by, db)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{draft_id}/reject", response_model=DraftReplyResponse)
async def reject(draft_id: int, reviewed_by: str = "agent", db: Session = Depends(get_db)):
    try:
        draft = reject_draft(draft_id, reviewed_by, db)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{draft_id}/edit", response_model=DraftReplyResponse)
async def edit(
    draft_id: int,
    edited_content: str,
    reviewed_by: str = "agent",
    db: Session = Depends(get_db),
):
    try:
        draft = edit_draft(draft_id, edited_content, reviewed_by, db)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pending/all", response_model=list[DraftReplyResponse])
async def get_pending_drafts(db: Session = Depends(get_db)):
    drafts = db.query(DraftReply).filter(
        DraftReply.status == "pending"
    ).order_by(DraftReply.created_at.desc()).all()
    return drafts
