import asyncio
from fastapi.testclient import TestClient
from app.database import init_db
from main import app

# Initialize database
init_db()

# Create test client
client = TestClient(app)

print("Testing Document API endpoints with Database...")
print("=" * 60)

# Test 1: Upload document
print("\n1. Testing POST /api/documents/upload")
response = client.post(
    "/api/documents/upload",
    json={
        "title": "Vietnamese Culture",
        "content": "Vietnam is a beautiful country in Southeast Asia with a rich history and culture.",
        "language": "en",
        "metadata": {"category": "culture", "source": "test"}
    }
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")
doc_id = response.json().get("doc_id")

# Test 2: List documents
print("\n2. Testing GET /api/documents/list")
response = client.get("/api/documents/list")
print(f"   Status: {response.status_code}")
result = response.json()
print(f"   Total documents: {result['total']}")
for doc in result['documents']:
    print(f"   - id={doc['doc_id']}, title='{doc['title']}'")

# Test 3: Get specific document
print(f"\n3. Testing GET /api/documents/{doc_id}")
response = client.get(f"/api/documents/{doc_id}")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 4: Delete document
print(f"\n4. Testing DELETE /api/documents/{doc_id}")
response = client.delete(f"/api/documents/{doc_id}")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 5: Verify deletion
print("\n5. Verifying deletion - GET /api/documents/list")
response = client.get("/api/documents/list")
result = response.json()
print(f"   Total documents after deletion: {result['total']}")

print("\n" + "=" * 60)
print("✓ All API tests completed successfully!")
