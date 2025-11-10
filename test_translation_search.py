import requests

# Test with "tài liệu về dịch thuật"
r = requests.post('http://127.0.0.1:8000/api/search/web', 
                  json={'query': 'tài liệu về dịch thuật', 'limit': 5})
d = r.json()
print(f"Query: 'tài liệu về dịch thuật'")
print(f"Limit: 5, Results returned: {len(d['results'])}, Total: {d['total_results']}")
for i, res in enumerate(d['results']):
    print(f"  {i+1}. {res['title']} ({res['source']})")

print("\n" + "="*60 + "\n")

# Test with "dịch thuật"
r = requests.post('http://127.0.0.1:8000/api/search/web', 
                  json={'query': 'dịch thuật', 'limit': 5})
d = r.json()
print(f"Query: 'dịch thuật'")
print(f"Results: {len(d['results'])}")
for i, res in enumerate(d['results']):
    print(f"  {i+1}. {res['title']} ({res['source']})")
