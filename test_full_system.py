import requests
import json

print("\n" + "=" * 70)
print("🚀 FULL SYSTEM TEST - Machine Translation & Document Search")
print("=" * 70)

# Test 1: Translation
print("\n" + "─" * 70)
print("1️⃣ TRANSLATION TEST")
print("─" * 70)

translation_tests = [
    ("Hello, how are you today?", "en", "vi"),
    ("Bạn đã ăn cơm chưa?", "vi", "en"),
    ("I am learning FastAPI", "en", "vi")
]

for text, src, tgt in translation_tests:
    try:
        r = requests.post(
            "http://localhost:8000/api/translate",
            json={"text": text, "source_lang": src, "target_lang": tgt},
            timeout=10
        )
        if r.status_code == 200:
            result = r.json()
            print(f"\n✅ {src.upper()} → {tgt.upper()}")
            print(f"   📝 Input:  {result['original_text']}")
            print(f"   🎯 Output: {result['translated_text']}")
        else:
            print(f"\n❌ Error: {r.status_code}")
    except Exception as e:
        print(f"\n❌ Exception: {e}")

# Test 2: Document List
print("\n" + "─" * 70)
print("2️⃣ DOCUMENT LISTING TEST")
print("─" * 70)

try:
    r = requests.get("http://localhost:8000/api/documents/list", timeout=10)
    if r.status_code == 200:
        docs = r.json()
        if isinstance(docs, dict):
            doc_list = docs.get('documents', []) if 'documents' in docs else [docs]
        else:
            doc_list = docs
        
        print(f"\n✅ Found {len(doc_list)} documents:")
        for i, doc in enumerate(doc_list[:3], 1):
            if isinstance(doc, dict):
                print(f"\n   {i}. {doc.get('title', 'N/A')}")
                print(f"      ID: {doc.get('doc_id', 'N/A')}")
            else:
                print(f"   {i}. {doc}")
    else:
        print(f"\n❌ Error: {r.status_code}")
except Exception as e:
    print(f"\n❌ Exception: {e}")

# Test 3: System Status
print("\n" + "─" * 70)
print("3️⃣ SYSTEM STATUS")
print("─" * 70)

endpoints = [
    ("Docs", "/docs"),
    ("API Root", "/api"),
    ("Health", "/health")
]

for name, endpoint in endpoints:
    try:
        r = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
        status_emoji = "✅" if r.status_code == 200 else "⚠️"
        print(f"{status_emoji} {name}: {r.status_code}")
    except:
        print(f"❌ {name}: Connection failed")

print("\n" + "=" * 70)
print("✨ System is running! Access at http://localhost:8000")
print("=" * 70 + "\n")
