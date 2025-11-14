from app.database import SessionLocal, init_db
from app.models.db_models import Document
from sqlmodel import select

# Initialize DB
init_db()

# Test insert
with SessionLocal() as session:
    # Insert test document
    doc1 = Document(
        title="Test Document",
        content="This is a test document for Vietnamese translation",
        language="en",
        doc_metadata={"source": "test", "category": "demo"}
    )
    session.add(doc1)
    session.commit()
    session.refresh(doc1)
    print(f"✓ Inserted document: id={doc1.id}, title='{doc1.title}'")
    
    # Query all documents
    docs = session.exec(select(Document)).all()
    print(f"✓ Query result: {len(docs)} documents in database")
    for doc in docs:
        print(f"  - id={doc.id}, title='{doc.title}', language='{doc.language}', created_at={doc.created_at}")
    
    # Get specific document
    retrieved = session.get(Document, 1)
    if retrieved:
        print(f"✓ Retrieved document by id: '{retrieved.title}'")
    
    # Update document
    retrieved.title = "Updated Title"
    session.add(retrieved)
    session.commit()
    session.refresh(retrieved)
    print(f"✓ Updated document: new title='{retrieved.title}'")

print("\n✓ All database tests passed!")
