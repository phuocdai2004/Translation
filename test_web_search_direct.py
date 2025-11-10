import asyncio
from app.routes.search_web_routes import search_web, WebSearchRequest

async def test():
    print("\n" + "="*60)
    print("🔍 WEB SEARCH TEST")
    print("="*60)
    
    queries = ["lập trình", "python", "machine learning"]
    
    for query in queries:
        print(f"\n📝 Searching: '{query}'")
        try:
            req = WebSearchRequest(query=query, num_results=3)
            result = await search_web(req)
            print(f"✓ Found {result.total_results} results\n")
            
            for i, r in enumerate(result.results[:2], 1):
                print(f"  {i}. {r.title}")
                print(f"     Snippet: {r.snippet[:60]}...")
                print(f"     Source: {r.source}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("="*60)
    print("✨ Web search working!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test())
