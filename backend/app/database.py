"""
Database configuration and session management
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Text, JSON, LargeBinary
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Database URL — SQLite by default, can override with env var
DB_FILE = os.environ.get("APP_DB", "documents.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Create engine with SQLite-specific settings
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debug logging
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False
)


def init_db():
    """Initialize database tables using raw SQL"""
    try:
        with engine.begin() as conn:
            # Create Document table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS document (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(255),
                    content TEXT NOT NULL,
                    language VARCHAR(50) NOT NULL DEFAULT 'vi',
                    doc_metadata JSON,
                    embedding BLOB,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_document_language ON document(language)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_document_title ON document(title)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_document_created_at ON document(created_at)"))
        
        logger.info(f"Database initialized at {DB_FILE}")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to inject session"""
    with SessionLocal() as session:
        yield session
