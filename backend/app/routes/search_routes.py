"""
Document search API routes
"""

from fastapi import APIRouter, HTTPException, Depends
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.document import SearchRequest, SearchResponse, SearchResult
from app.database import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest, session: Session = Depends(get_session)):
    # Lazy import to avoid loading transformers/torch at startup
    from app.services.embedding_service import get_embedding, search_index
    from app.utils.embedding_utils import deserialize_embedding
    """
    Search documents using semantic similarity (FAISS)
    
    ### Parameters:
    - **query**: Search query text
    - **top_k**: Number of results to return (default: 5)
    - **language**: Search language (default: "en")
    
    ### Returns:
    - **query**: Original search query
    - **results**: List of matching documents with scores
    - **total_results**: Total number of results
    - **processing_time**: Time taken to process search
    """
    try:
        start_time = time.time()
        logger.info(f"Searching for: {request.query}")
        
        # Generate embedding for query
        query_embedding = get_embedding(request.query)
        if query_embedding is None:
            logger.warning("Could not generate query embedding")
            return SearchResponse(
                query=request.query,
                results=[],
                total_results=0,
                processing_time=time.time() - start_time
            )
        
        # Search FAISS index
        search_results = search_index(query_embedding, request.top_k)
        
        if not search_results:
            logger.info("No results found in FAISS index")
            return SearchResponse(
                query=request.query,
                results=[],
                total_results=0,
                processing_time=time.time() - start_time
            )
        
        # Fetch document details from DB
        results = []
        for doc_id, similarity_score in search_results:
            try:
                result = session.execute(
                    text("SELECT id, title, content FROM document WHERE id = :id"),
                    {"id": doc_id}
                )
                row = result.fetchone()
                if row:
                    results.append(
                        SearchResult(
                            doc_id=row[0],
                            title=row[1] or "Untitled",
                            content=row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                            score=round(similarity_score, 3)
                        )
                    )
            except Exception as e:
                logger.error(f"Error fetching document {doc_id}: {e}")
        
        processing_time = time.time() - start_time
        logger.info(f"✓ Search completed: {len(results)} results in {processing_time:.2f}s")
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search/stats")
async def get_search_stats(session: Session = Depends(get_session)):
    """Get search statistics"""
    try:
        result = session.execute(text("SELECT COUNT(*) FROM document"))
        total_docs = result.scalar()
        
        result = session.execute(
            text("SELECT COUNT(*) FROM document WHERE embedding IS NOT NULL")
        )
        indexed_docs = result.scalar()
        
        return {
            "total_documents": total_docs or 0,
            "indexed_documents": indexed_docs or 0,
            "faiss_enabled": True
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "total_documents": 0,
            "indexed_documents": 0,
            "faiss_enabled": False,
            "error": str(e)
        }
