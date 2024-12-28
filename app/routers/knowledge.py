from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import KnowledgeDocument
from app.services.rag_service import add_document, query_knowledge_base

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/documents")
async def upload_document(
    title: str,
    doc_type: str,
    source: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    content_str = content.decode("utf-8")

    doc = KnowledgeDocument(
        title=title,
        source=source,
        content=content_str,
        doc_type=doc_type,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunks = add_document(
        doc_id=f"doc_{doc.id}",
        content=content_str,
        metadata={"source": source, "doc_type": doc_type, "title": title},
    )

    return {
        "id": doc.id,
        "title": title,
        "chunks_created": chunks,
        "status": "geladen",
    }


@router.get("/search")
async def search_knowledge(query: str, n_results: int = 3):
    results = query_knowledge_base(query, n_results)
    if not results:
        raise HTTPException(status_code=404, detail="Geen relevante informatie gevonden")
    return {"query": query, "context": results}


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDocument).all()
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "source": doc.source,
            "doc_type": doc.doc_type,
            "created_at": doc.created_at,
        }
        for doc in docs
    ]
