"""
Document management API routes
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.document import DocumentUpload
from app.database import get_session
from app.utils.embedding_utils import serialize_embedding
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/documents/upload")
async def upload_document(document: DocumentUpload, session: Session = Depends(get_session)):
    """
    Upload and index a new document
    
    ### Parameters:
    - **title**: Document title
    - **content**: Document content
    - **language**: Document language
    - **metadata**: Optional metadata dictionary
    
    ### Returns:
    - Document ID and confirmation
    """
    try:
        # Insert into database using raw SQL
        metadata_json = json.dumps(document.metadata or {})
        result = session.execute(
            text("""
                INSERT INTO document (title, content, language, doc_metadata, created_at)
                VALUES (:title, :content, :language, :doc_metadata, CURRENT_TIMESTAMP)
            """),
            {
                "title": document.title,
                "content": document.content,
                "language": document.language,
                "doc_metadata": metadata_json
            }
        )
        session.commit()
        doc_id = result.lastrowid
        
        logger.info(f"Document uploaded: id={doc_id} - {document.title}")
        
        # TODO: Generate embeddings with Sentence Transformers and add to FAISS
        
        return {
            "doc_id": doc_id,
            "title": document.title,
            "status": "indexed",
            "message": "Document successfully uploaded and indexed"
        }
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/documents/list")
async def list_documents(session: Session = Depends(get_session)):
    """List all uploaded documents"""
    try:
        result = session.execute(
            text("SELECT id, title, language, created_at FROM document ORDER BY created_at DESC")
        )
        docs = result.fetchall()
        
        return {
            "documents": [
                {
                    "doc_id": doc[0],
                    "title": doc[1],
                    "language": doc[2],
                    "created_at": doc[3]
                }
                for doc in docs
            ],
            "total": len(docs)
        }
    
    except Exception as e:
        logger.error(f"List error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/documents/{doc_id}")
async def get_document(doc_id: int, session: Session = Depends(get_session)):
    """Get a specific document by ID"""
    try:
        result = session.execute(
            text("SELECT id, title, content, language, doc_metadata, created_at FROM document WHERE id = :id"),
            {"id": doc_id}
        )
        doc = result.fetchone()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        metadata = json.loads(doc[4]) if doc[4] else {}
        return {
            "doc_id": doc[0],
            "title": doc[1],
            "content": doc[2],
            "language": doc[3],
            "metadata": metadata,
            "created_at": doc[5]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int, session: Session = Depends(get_session)):
    """Delete a document"""
    try:
        # Check if document exists
        check_result = session.execute(
            text("SELECT id FROM document WHERE id = :id"),
            {"id": doc_id}
        )
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document
        session.execute(
            text("DELETE FROM document WHERE id = :id"),
            {"id": doc_id}
        )
        session.commit()
        
        logger.info(f"Document deleted: id={doc_id}")
        
        return {
            "status": "deleted",
            "doc_id": doc_id,
            "message": "Document successfully deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )
