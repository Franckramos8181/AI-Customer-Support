from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, get_db
from app.models import Conversation, DraftReply
from app.routers import messages, knowledge, drafts

app = FastAPI(title=settings.app_title, version="0.1.0")

app.include_router(messages.router)
app.include_router(knowledge.router)
app.include_router(drafts.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_title}


@app.get("/api/status")
async def api_status():
    return {
        "status": "running",
        "version": "0.1.0",
        "service": settings.app_title,
    }


@app.get("/dashboard")
async def dashboard(request: Request, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Conversation)
    if status:
        query = query.filter(Conversation.status == status)
    conversations = query.order_by(Conversation.updated_at.desc()).all()

    stats = {
        "total": db.query(Conversation).count(),
        "open": db.query(Conversation).filter(Conversation.status == "open").count(),
        "in_progress": db.query(Conversation).filter(Conversation.status == "in_progress").count(),
        "resolved": db.query(Conversation).filter(Conversation.status == "resolved").count(),
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "conversations": conversations,
        "stats": stats,
        "current_filter": status,
    })


@app.get("/dashboard/conversation/{conversation_id}")
async def conversation_detail(request: Request, conversation_id: int, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "conversations": [],
            "stats": {},
            "current_filter": None,
        })

    conversation_drafts = db.query(DraftReply).filter(
        DraftReply.conversation_id == conversation_id
    ).order_by(DraftReply.created_at.desc()).all()

    return templates.TemplateResponse("conversation.html", {
        "request": request,
        "conversation": conversation,
        "drafts": conversation_drafts,
    })


@app.get("/dashboard/pending")
async def pending_reviews(request: Request, db: Session = Depends(get_db)):
    conversations_with_pending = db.query(Conversation).join(DraftReply).filter(
        DraftReply.status == "pending"
    ).all()

    stats = {
        "total": db.query(Conversation).count(),
        "open": db.query(Conversation).filter(Conversation.status == "open").count(),
        "in_progress": db.query(Conversation).filter(Conversation.status == "in_progress").count(),
        "resolved": db.query(Conversation).filter(Conversation.status == "resolved").count(),
    }

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "conversations": conversations_with_pending,
        "stats": stats,
        "current_filter": "pending",
    })
