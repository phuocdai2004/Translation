"""
Embedding and vector index management using Annoy
Simpler alternative to FAISS for semantic search
"""

import logging
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
import json
import threading

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import annoy
    EMBEDDINGS_AVAILABLE = True
except ImportError as e:
    EMBEDDINGS_AVAILABLE = False
    logger.warning(f"Embeddings not available: {e}")

# Global embedding model (lazy load)
embedding_model = None
annoy_index = None
index_lock = threading.Lock()  # Thread safety for index updates

INDEX_DIR = Path("data")
INDEX_PATH = INDEX_DIR / "annoy.index"
MAPPING_PATH = INDEX_DIR / "doc_mapping.json"


def init_embeddings():
    """Initialize embedding model (lazy load on first use)"""
    global embedding_model
    if embedding_model is None and EMBEDDINGS_AVAILABLE:
        try:
            logger.info("Loading sentence-transformers model...")
            embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info(f"✓ Embedding model loaded: {embedding_model.get_sentence_embedding_dimension()} dims")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            embedding_model = None
    return embedding_model


def get_embedding(text: str) -> Optional[np.ndarray]:
    """Get embedding for text"""
    if not EMBEDDINGS_AVAILABLE:
        return None
    
    model = init_embeddings()
    if model is None:
        return None
    
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None


def init_index_dir():
    """Ensure data directory exists"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load_or_create_index(embedding_dim: int = 384):
    """Load existing index or create new one"""
    global annoy_index
    
    if annoy_index is not None:
        return annoy_index
    
    if not EMBEDDINGS_AVAILABLE:
        logger.warning("Embeddings not available, skipping index load")
        return None
    
    init_index_dir()
    
    try:
        if INDEX_PATH.exists():
            logger.info(f"Loading Annoy index from {INDEX_PATH}")
            annoy_index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
            annoy_index.load(str(INDEX_PATH))
            logger.info(f"✓ Index loaded: {annoy_index.get_n_items()} vectors")
            return annoy_index
    except Exception as e:
        logger.error(f"Error loading index: {e}")
    
    # Create new index
    logger.info(f"Creating new Annoy index (dim={embedding_dim}, metric=euclidean)")
    annoy_index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
    logger.info("✓ New index created")
    return annoy_index


def add_to_index(doc_id: int, embedding: np.ndarray) -> bool:
    """Add embedding to Annoy index with thread safety"""
    if not EMBEDDINGS_AVAILABLE:
        return False
    
    try:
        with index_lock:
            # Don't load existing index — create new one for fresh adds
            # Annoy doesn't allow adding items to loaded indexes
            embedding_dim = len(embedding)
            
            # Try to load existing mapping
            if MAPPING_PATH.exists():
                with open(MAPPING_PATH, "r") as f:
                    doc_ids = json.load(f)
                # Load existing index to get all vectors
                try:
                    init_index_dir()
                    index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
                    if INDEX_PATH.exists():
                        index.load(str(INDEX_PATH))
                    
                    # Get all existing vectors from DB and rebuild
                    from sqlalchemy import text
                    # Can't access session here — rebuild instead
                except:
                    index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
                    doc_ids = []
            else:
                doc_ids = []
                index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
            
            # Add new vector
            vector_idx = index.get_n_items()
            index.add_item(vector_idx, embedding)
            
            # Append doc_id
            doc_ids.append(doc_id)
            
            # Build index
            index.build(10)  # 10 trees
            
            # Save
            init_index_dir()
            with open(MAPPING_PATH, "w") as f:
                json.dump(doc_ids, f)
            index.save(str(INDEX_PATH))
            
            # Reset global
            global annoy_index
            annoy_index = None
            
            logger.info(f"+ Added doc_id={doc_id} to index (total: {index.get_n_items()})")
            return True
    except Exception as e:
        logger.error(f"Error adding to index: {e}")
        return False


def search_index(query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
    """
    Search Annoy index
    Returns list of (doc_id, similarity_score) tuples
    """
    if not EMBEDDINGS_AVAILABLE or not MAPPING_PATH.exists():
        return []
    
    try:
        with index_lock:
            index = load_or_create_index(len(query_embedding))
            if index is None:
                return []
            
            n_items = index.get_n_items()
            if n_items == 0:
                return []
            
            # Search - Annoy returns (indices_list, distances_list)
            result = index.get_nns_by_vector(
                query_embedding,
                min(top_k, n_items),
                include_distances=True
            )
            
            indices, distances = result
            
            # Load mapping
            with open(MAPPING_PATH, "r") as f:
                doc_ids = json.load(f)
            
            # Convert distances to similarity scores
            results = []
            for idx, distance in zip(indices, distances):
                if idx < len(doc_ids):
                    doc_id = doc_ids[int(idx)]
                    # Convert euclidean distance to similarity (inverse)
                    similarity = 1.0 / (1.0 + float(distance))
                    results.append((doc_id, similarity))
            
            return results
    except Exception as e:
        logger.error(f"Error searching index: {e}")
        return []


def rebuild_index_from_db(session):
    """Rebuild Annoy index from database embeddings"""
    if not EMBEDDINGS_AVAILABLE:
        logger.warning("Embeddings not available, skipping index rebuild")
        return
    
    try:
        from sqlalchemy import text
        
        with index_lock:
            # Get all documents with embeddings
            result = session.execute(
                text("SELECT id, embedding FROM document WHERE embedding IS NOT NULL ORDER BY id")
            )
            rows = result.fetchall()
            
            if not rows:
                logger.info("No documents with embeddings to rebuild index")
                return
            
            # Create new index
            embedding_dim = 384  # all-MiniLM-L6-v2 dimension
            index = annoy.AnnoyIndex(embedding_dim, metric='euclidean')
            doc_ids = []
            
            # Rebuild
            from app.utils.embedding_utils import deserialize_embedding
            for vector_idx, (doc_id, embedding_bytes) in enumerate(rows):
                embedding = deserialize_embedding(embedding_bytes)
                if embedding is not None:
                    index.add_item(vector_idx, embedding)
                    doc_ids.append(doc_id)
            
            # Build
            index.build(10)
            
            # Save
            init_index_dir()
            index.save(str(INDEX_PATH))
            with open(MAPPING_PATH, "w") as f:
                json.dump(doc_ids, f)
            
            logger.info(f"✓ Index rebuilt: {index.get_n_items()} vectors from {len(doc_ids)} documents")
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")


def cleanup_index():
    """Remove index files (for testing/cleanup)"""
    try:
        global annoy_index
        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if MAPPING_PATH.exists():
            MAPPING_PATH.unlink()
        annoy_index = None
        logger.info("✓ Cleaned up index files")
    except Exception as e:
        logger.error(f"Error cleaning up index: {e}")
