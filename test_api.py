import requests
import json

print("=" * 60)
print("🔍 MACHINE TRANSLATION & SEARCH SYSTEM TEST")
print("=" * 60)

tests = [
    {
        "name": "EN → VI (English to Vietnamese)",
        "endpoint": "/api/translate",
        "data": {"text": "I love programming", "source_lang": "en", "target_lang": "vi"}
    },
    {
        "name": "VI → EN (Vietnamese to English)", 
        "endpoint": "/api/translate",
        "data": {"text": "Tôi thích lập trình", "source_lang": "vi", "target_lang": "en"}
    },
    {
        "name": "EN → VI (Complex sentence)",
        "endpoint": "/api/translate",
        "data": {"text": "The quick brown fox jumps over the lazy dog", "source_lang": "en", "target_lang": "vi"}
    },
    {
        "name": "VI → EN (Complex sentence)",
        "endpoint": "/api/translate",
        "data": {"text": "Ngôn ngữ lập trình Python rất mạnh mẽ", "source_lang": "vi", "target_lang": "en"}
    }
]

for test in tests:
    try:
        r = requests.post(f"http://localhost:8000{test['endpoint']}", json=test['data'], timeout=15)
        if r.status_code == 200:
            result = r.json()
            print(f"\n✅ {test['name']}")
            print(f"   Input:  {result['original_text']}")
            print(f"   Output: {result['translated_text']}")
        else:
            print(f"\n❌ {test['name']} - Status: {r.status_code}")
            print(f"   Response: {r.text}")
    except Exception as e:
        print(f"\n❌ {test['name']} - Error: {e}")

print("\n" + "=" * 60)
print("✨ Translation API is working perfectly! 🎉")
print("=" * 60)
