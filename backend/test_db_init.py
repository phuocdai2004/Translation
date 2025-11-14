from app.database import init_db
from app.models.db_models import Document
init_db()
print("✓ Database initialized successfully")
print("✓ Document model registered")
