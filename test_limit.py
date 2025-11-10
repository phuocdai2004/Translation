import requests

# Test limit parameter
r = requests.post('http://127.0.0.1:8000/api/search/web', 
                  json={'query': 'python', 'limit': 2})
d = r.json()
print(f"Limit: 2, Results returned: {len(d['results'])}, Total: {d['total_results']}")
for i, res in enumerate(d['results']):
    print(f"  {i+1}. {res['title']}")

# Test with limit=3
r = requests.post('http://127.0.0.1:8000/api/search/web', 
                  json={'query': 'machine learning', 'limit': 1})
d = r.json()
print(f"\nLimit: 1, Results returned: {len(d['results'])}, Total: {d['total_results']}")
for i, res in enumerate(d['results']):
    print(f"  {i+1}. {res['title']}")
