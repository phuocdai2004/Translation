"""
Utility functions for embedding serialization and FAISS index management
"""

import numpy as np
import io
import json
import logging
from pathlib import Path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# FAISS index and mapping storage paths
INDEX_DIR = Path("data")
INDEX_PATH = INDEX_DIR / "faiss.index"
MAPPING_PATH = INDEX_DIR / "doc_mapping.json"


def serialize_embedding(vec: np.ndarray) -> bytes:
    """
    Serialize numpy array to bytes using .npy format.
    
    Args:
        vec: numpy array (float32)
    
    Returns:
        bytes: serialized array
    """
    if vec is None:
        return None
    
    try:
        buf = io.BytesIO()
        np.save(buf, vec.astype(np.float32), allow_pickle=False)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Embedding serialization error: {e}")
        return None


def deserialize_embedding(data: bytes) -> Optional[np.ndarray]:
    """
    Deserialize bytes back to numpy array.
    
    Args:
        data: bytes from database
    
    Returns:
        numpy array or None if invalid
    """
    if data is None:
        return None
    
    try:
        buf = io.BytesIO(data)
        buf.seek(0)
        arr = np.load(buf, allow_pickle=False)
        return arr.astype(np.float32)
    except Exception as e:
        logger.error(f"Embedding deserialization error: {e}")
        return None


def init_index_dir():
    """Ensure data directory exists"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def save_doc_mapping(doc_ids: List[int]):
    """
    Save document ID mapping for FAISS index.
    
    doc_ids[i] = document id that corresponds to FAISS vector at position i
    """
    init_index_dir()
    try:
        with open(MAPPING_PATH, "w") as f:
            json.dump(doc_ids, f)
        logger.info(f"Saved doc mapping: {len(doc_ids)} docs")
    except Exception as e:
        logger.error(f"Error saving doc mapping: {e}")


def load_doc_mapping() -> List[int]:
    """Load document ID mapping from disk"""
    try:
        if MAPPING_PATH.exists():
            with open(MAPPING_PATH, "r") as f:
                mapping = json.load(f)
            logger.info(f"Loaded doc mapping: {len(mapping)} docs")
            return mapping
    except Exception as e:
        logger.error(f"Error loading doc mapping: {e}")
    return []


def cleanup_index():
    """Remove index files (for cleanup/rebuild)"""
    try:
        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if MAPPING_PATH.exists():
            MAPPING_PATH.unlink()
        logger.info("Cleaned up FAISS index files")
    except Exception as e:
        logger.error(f"Error cleaning up index: {e}")
