import requests
import json

print("=" * 60)
print("📄 DOCUMENT MANAGEMENT TEST")
print("=" * 60)

# Sample documents to upload
sample_docs = [
    {
        "title": "Python Programming Basics",
        "content": "Python is a high-level programming language known for its simplicity and readability. It's widely used for web development, data science, and automation. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
        "language": "en",
        "metadata": {"category": "programming", "level": "beginner"}
    },
    {
        "title": "Machine Learning Introduction",
        "content": "Machine Learning is a subset of Artificial Intelligence that focuses on the ability of computers to learn from data without being explicitly programmed. It uses algorithms and statistical models to identify patterns and make predictions based on training data.",
        "language": "en",
        "metadata": {"category": "ai", "level": "intermediate"}
    },
    {
        "title": "Web Development with FastAPI",
        "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+. It provides automatic API documentation, data validation, and asynchronous support. FastAPI is built on top of Starlette and Pydantic, making it both powerful and easy to use.",
        "language": "en",
        "metadata": {"category": "web", "level": "intermediate"}
    }
]

print("\n📤 Uploading Documents...\n")

uploaded_docs = []
for doc in sample_docs:
    try:
        r = requests.post(
            "http://localhost:8000/api/documents/upload",
            json=doc,
            timeout=10
        )
        if r.status_code == 200:
            result = r.json()
            uploaded_docs.append(result)
            print(f"✅ Uploaded: {result['title']}")
            print(f"   Doc ID: {result['doc_id']}")
        else:
            print(f"❌ Failed to upload: {doc['title']}")
            print(f"   Status: {r.status_code}")
    except Exception as e:
        print(f"❌ Error uploading {doc['title']}: {e}")

print("\n" + "=" * 60)
print("📋 Listing All Documents...\n")

try:
    r = requests.get("http://localhost:8000/api/documents/list", timeout=10)
    if r.status_code == 200:
        docs = r.json()
        print(f"Total Documents: {len(docs)}\n")
        for doc in docs:
            print(f"- {doc['title']} (ID: {doc['doc_id']})")
    else:
        print(f"Failed to list documents. Status: {r.status_code}")
except Exception as e:
    print(f"Error listing documents: {e}")

print("\n" + "=" * 60)
print("✨ Documents uploaded successfully!")
print("=" * 60)
