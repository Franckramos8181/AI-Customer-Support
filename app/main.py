from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import init_db
from app.routers import messages

app = FastAPI(title=settings.app_title, version="0.1.0")

app.include_router(messages.router)

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
