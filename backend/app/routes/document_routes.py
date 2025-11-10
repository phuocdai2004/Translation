"""
Document management API routes
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
import logging
from typing import List
from app.models.document import DocumentUpload

router = APIRouter()
logger = logging.getLogger(__name__)

# Temporary in-memory document store
documents = {}
doc_counter = 0


@router.post("/documents/upload")
async def upload_document(document: DocumentUpload):
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
    global doc_counter
    try:
        doc_counter += 1
        doc_id = f"doc_{doc_counter}"
        
        documents[doc_id] = {
            "title": document.title,
            "content": document.content,
            "language": document.language,
            "metadata": document.metadata or {}
        }
        
        logger.info(f"Document uploaded: {doc_id} - {document.title}")
        
        # TODO: Index document with embeddings using Sentence Transformers
        
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
async def list_documents():
    """List all uploaded documents"""
    try:
        docs = []
        for doc_id, doc_data in documents.items():
            docs.append({
                "doc_id": doc_id,
                "title": doc_data["title"],
                "language": doc_data["language"]
            })
        
        return {
            "documents": docs,
            "total": len(docs)
        }
    
    except Exception as e:
        logger.error(f"List error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID"""
    try:
        if doc_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc = documents[doc_id]
        return {
            "doc_id": doc_id,
            "title": doc["title"],
            "content": doc["content"],
            "language": doc["language"],
            "metadata": doc["metadata"]
        }
    
    except Exception as e:
        logger.error(f"Get error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    try:
        if doc_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        del documents[doc_id]
        logger.info(f"Document deleted: {doc_id}")
        
        return {
            "status": "deleted",
            "doc_id": doc_id,
            "message": "Document successfully deleted"
        }
    
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )
