"""
Test embedding + semantic search integration
"""
import sys
import os
# Set env var for better compatibility
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Testing Semantic Search with Embeddings and FAISS...")
print("=" * 70)

# Clean up old data BEFORE initializing DB
try:
    if os.path.exists("documents.db"):
        os.remove("documents.db")
        print("✓ Cleaned old database")
    # Also clean index
    import shutil
    if os.path.exists("data"):
        shutil.rmtree("data")
        print("✓ Cleaned old index")
except Exception as e:
    print(f"Could not remove old data: {e}")

from fastapi.testclient import TestClient
from app.database import init_db
from main import app
import time

# Initialize database AFTER cleanup
init_db()

# Create test client
client = TestClient(app)

# Test 1: Upload documents
print("\n1. Uploading test documents...")
test_docs = [
    {
        "title": "Python Programming",
        "content": "Python is a high-level programming language. It is easy to learn and widely used in data science, web development, and artificial intelligence.",
        "language": "en"
    },
    {
        "title": "Machine Learning Basics",
        "content": "Machine learning is a subset of artificial intelligence. It enables computers to learn from data and make predictions without being explicitly programmed.",
        "language": "en"
    },
    {
        "title": "Web Development",
        "content": "Web development involves creating websites and web applications. It uses technologies like HTML, CSS, JavaScript, and backend frameworks.",
        "language": "en"
    }
]

uploaded_docs = []
for doc in test_docs:
    response = client.post("/api/documents/upload", json=doc)
    if response.status_code == 200:
        data = response.json()
        uploaded_docs.append(data["doc_id"])
        print(f"   + Uploaded: {data['title']} (id={data['doc_id']})")
    else:
        print(f"   - Failed to upload: {doc['title']}")
        print(f"     Error: {response.text}")

time.sleep(1)  # Wait for indexing

# Test 2: Search statistics
print("\n2. Checking search statistics...")
response = client.get("/api/search/stats")
if response.status_code == 200:
    stats = response.json()
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Indexed documents: {stats.get('indexed_documents', 0)}")
    print(f"   FAISS enabled: {stats.get('faiss_enabled', False)}")

# Test 3: Semantic search
print("\n3. Testing semantic search queries...")
search_queries = [
    ("machine learning algorithms", 2),
    ("python programming language", 2),
    ("web development frameworks", 2),
    ("data science and AI", 3),
]

for query, expected_results in search_queries:
    print(f"\n   Query: '{query}'")
    response = client.post(
        "/api/search",
        json={"query": query, "top_k": 3, "language": "en"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Results: {result['total_results']} docs (in {result['processing_time']:.3f}s)")
        for i, res in enumerate(result['results'], 1):
            print(f"     {i}. {res['title']} (score: {res['score']:.3f})")
    else:
        print(f"   ✗ Error: {response.status_code}")
        print(f"     {response.text}")

# Test 4: List documents
print("\n4. Listing all documents...")
response = client.get("/api/documents/list")
if response.status_code == 200:
    result = response.json()
    print(f"   Total: {result['total']} documents")
    for doc in result['documents']:
        print(f"   - {doc['title']} (id={doc['doc_id']})")

print("\n" + "=" * 70)
print("+ Semantic search integration test completed!")
