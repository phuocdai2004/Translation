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
    # Lazy import to avoid loading transformers/torch at startup
    from app.utils.embedding_utils import serialize_embedding
    from app.services.embedding_service import get_embedding, add_to_index
    
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
        
        # Generate embedding and add to FAISS index
        embedding = get_embedding(document.content)
        if embedding is not None:
            embedding_bytes = serialize_embedding(embedding)
            
            # Save embedding to database
            session.execute(
                text("UPDATE document SET embedding = :embedding WHERE id = :id"),
                {"embedding": embedding_bytes, "id": doc_id}
            )
            session.commit()
            
            # Add to FAISS index
            add_to_index(doc_id, embedding)
            logger.info(f"✓ Embedding created and indexed for doc_id={doc_id}")
        else:
            logger.warning(f"Could not generate embedding for doc_id={doc_id}")
        
        logger.info(f"Document uploaded: id={doc_id} - {document.title}")
        
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


@router.put("/documents/{doc_id}")
async def update_document(doc_id: int, document: DocumentUpload, session: Session = Depends(get_session)):
    """Edit/Update a document"""
    from app.utils.embedding_utils import serialize_embedding
    from app.services.embedding_service import get_embedding, add_to_index
    
    try:
        # Check if document exists
        check_result = session.execute(
            text("SELECT id FROM document WHERE id = :id"),
            {"id": doc_id}
        )
        if not check_result.fetchone():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update document
        metadata_json = json.dumps(document.metadata or {})
        session.execute(
            text("""
                UPDATE document 
                SET title = :title, content = :content, language = :language, doc_metadata = :doc_metadata
                WHERE id = :id
            """),
            {
                "title": document.title,
                "content": document.content,
                "language": document.language,
                "doc_metadata": metadata_json,
                "id": doc_id
            }
        )
        session.commit()
        
        # Re-generate embedding
        embedding = get_embedding(document.content)
        if embedding is not None:
            embedding_bytes = serialize_embedding(embedding)
            session.execute(
                text("UPDATE document SET embedding = :embedding WHERE id = :id"),
                {"embedding": embedding_bytes, "id": doc_id}
            )
            session.commit()
            add_to_index(doc_id, embedding)
            logger.info(f"✓ Embedding updated for doc_id={doc_id}")
        
        logger.info(f"Document updated: id={doc_id} - {document.title}")
        
        return {
            "doc_id": doc_id,
            "title": document.title,
            "status": "updated",
            "message": "Document successfully updated and re-indexed"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update document: {str(e)}"
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
