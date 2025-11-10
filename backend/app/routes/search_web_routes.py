"""
Web Search API routes - Free web search with fallback data
"""

from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel
import requests
from typing import Optional, List

router = APIRouter()
logger = logging.getLogger(__name__)

# Fallback knowledge base with common search queries
KNOWLEDGE_BASE = {
    "python": [
        {"title": "Python Official Website", "link": "https://www.python.org", "snippet": "Official Python programming language website. Learn Python, download latest version."},
        {"title": "Python Tutorial | W3Schools", "link": "https://www.w3schools.com/python", "snippet": "Learn Python with examples and exercises. Complete tutorial from basics to advanced."},
        {"title": "Real Python - Python Tutorials", "link": "https://realpython.com", "snippet": "In-depth Python tutorials and guides. Learn web development and data science."},
        {"title": "Python Stack Overflow", "link": "https://stackoverflow.com/questions/tagged/python", "snippet": "Stack Overflow Q&A for Python. Find answers to common programming questions."},
        {"title": "Python Documentation", "link": "https://docs.python.org", "snippet": "Official Python documentation. API reference and language guides."},
    ],
    "machine learning": [
        {"title": "TensorFlow Official", "link": "https://www.tensorflow.org", "snippet": "Open source ML framework by Google. Build and train ML models easily."},
        {"title": "Scikit-learn", "link": "https://scikit-learn.org", "snippet": "Machine learning library for Python. Classification, regression, clustering and more."},
        {"title": "PyTorch Official", "link": "https://pytorch.org", "snippet": "Deep learning framework. Flexible and powerful for machine learning."},
        {"title": "Kaggle ML Courses", "link": "https://www.kaggle.com/learn", "snippet": "Free machine learning and data science courses on Kaggle."},
        {"title": "Andrew Ng ML Course", "link": "https://www.coursera.org/learn/machine-learning", "snippet": "Comprehensive machine learning course by Andrew Ng on Coursera."},
    ],
    "fastapi": [
        {"title": "FastAPI Official", "link": "https://fastapi.tiangolo.com", "snippet": "Modern fast web framework for building APIs with Python 3.7+."},
        {"title": "FastAPI GitHub", "link": "https://github.com/tiangolo/fastapi", "snippet": "FastAPI source code on GitHub. Open source project."},
        {"title": "FastAPI Tutorial", "link": "https://fastapi.tiangolo.com/tutorial", "snippet": "Step-by-step FastAPI tutorial. Learn to build APIs with auto documentation."},
        {"title": "FastAPI Best Practices", "link": "https://fastapi.tiangolo.com/deployment", "snippet": "FastAPI deployment and production best practices guide."},
    ],
    "lập trình": [
        {"title": "Học Lập Trình Python", "link": "https://www.python.org/", "snippet": "Python là ngôn ngữ lập trình mạnh mẽ, dễ học. Tuyệt vời cho người mới."},
        {"title": "W3Schools Python", "link": "https://www.w3schools.com/python", "snippet": "Hướng dẫn Python từ cơ bản đến nâng cao. Ví dụ minh họa và bài tập."},
        {"title": "Codecademy - Học Lập Trình", "link": "https://www.codecademy.com", "snippet": "Nền tảng học lập trình trực tuyến với các bài tập tương tác."},
        {"title": "freeCodeCamp Tutorials", "link": "https://www.freecodecamp.org", "snippet": "Các video hướng dẫn lập trình miễn phí từ freeCodeCamp."},
        {"title": "GeeksforGeeks", "link": "https://www.geeksforgeeks.org", "snippet": "Nguồn tài liệu lập trình toàn diện với các ví dụ chi tiết."},
    ],
    "dịch thuật": [
        {"title": "Google Translate", "link": "https://translate.google.com", "snippet": "Công cụ dịch thuật miễn phí từ Google. Hỗ trợ 100+ ngôn ngữ."},
        {"title": "DeepL Translator", "link": "https://www.deepl.com/translator", "snippet": "Công cụ dịch thuật AI hiện đại. Chính xác hơn Google Translate."},
        {"title": "Microsoft Translator", "link": "https://www.microsoft.com/en-us/translator", "snippet": "Dịch thuật từ Microsoft. API và công cụ trực tuyến."},
        {"title": "UNESCO - Dịch Thuật Máy", "link": "https://www.un.org", "snippet": "Tài liệu về công nghệ dịch thuật từ UNESCO."},
        {"title": "Machine Translation Evaluation", "link": "https://aclanthology.org", "snippet": "Nghiên cứu và đánh giá công nghệ dịch thuật máy."},
    ],
    "tài liệu": [
        {"title": "Wikipedia", "link": "https://www.wikipedia.org", "snippet": "Bách khoa toàn thư trực tuyến miễn phí với hàng triệu bài viết."},
        {"title": "Project Gutenberg", "link": "https://www.gutenberg.org", "snippet": "Kho sách điện tử miễn phí với hơn 70,000 cuốn sách."},
        {"title": "Archive.org", "link": "https://archive.org", "snippet": "Kho lưu trữ số kỹ thuật số. Sách, âm thanh, video và hơn thế nữa."},
        {"title": "Google Scholar", "link": "https://scholar.google.com", "snippet": "Công cụ tìm kiếm học thuật cho các bài báo khoa học."},
        {"title": "ResearchGate", "link": "https://www.researchgate.net", "snippet": "Mạng xã hội cho các nhà khoa học và nghiên cứu viên."},
    ],
    "data science": [
        {"title": "Pandas Documentation", "link": "https://pandas.pydata.org", "snippet": "Thư viện phân tích dữ liệu mạnh mẽ cho Python."},
        {"title": "NumPy Official", "link": "https://numpy.org", "snippet": "Thư viện tính toán số cho Python với hiệu suất cao."},
        {"title": "Matplotlib", "link": "https://matplotlib.org", "snippet": "Thư viện vẽ biểu đồ và trực quan hóa dữ liệu cho Python."},
        {"title": "Jupyter Notebook", "link": "https://jupyter.org", "snippet": "Môi trường tương tác cho khoa học dữ liệu và máy tính khoa học."},
        {"title": "Kaggle Datasets", "link": "https://www.kaggle.com/datasets", "snippet": "Kho dữ liệu công khai cho các dự án khoa học dữ liệu."},
    ],
}

class WebSearchRequest(BaseModel):
    """Model for web search request"""
    query: str
    limit: Optional[int] = 5
    language: Optional[str] = "en"

class SearchResult(BaseModel):
    """Model for search result"""
    title: str
    link: str
    snippet: str
    source: str = "Web"

class WebSearchResponse(BaseModel):
    """Model for web search response"""
    query: str
    results: List[SearchResult]
    total_results: int


@router.post("/web", response_model=WebSearchResponse)
async def search_web(request: WebSearchRequest):
    """
    Search the web using free sources (DuckDuckGo API + fallback knowledge base)
    """
    try:
        logger.info(f"Web searching: {request.query}")
        
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        search_results = []
        query_lower = request.query.lower().strip()
        
        # Try DuckDuckGo API first
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            params = {
                "q": request.query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get("https://api.duckduckgo.com/", params=params, headers=headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("AbstractText") and data.get("AbstractURL"):
                    search_results.append(SearchResult(
                        title=data.get("Heading", "Result"),
                        link=data.get("AbstractURL", "#"),
                        snippet=data.get("AbstractText", ""),
                        source="DuckDuckGo"
                    ))
                
                for item in data.get("RelatedTopics", []):
                    if isinstance(item, dict) and item.get("FirstURL"):
                        search_results.append(SearchResult(
                            title=item.get("Text", "")[:100],
                            link=item.get("FirstURL", "#"),
                            snippet=item.get("Text", ""),
                            source="DuckDuckGo"
                        ))
                        if len(search_results) >= request.limit:
                            break
                
        except Exception as e:
            logger.warning(f"DuckDuckGo API error: {e}. Using fallback...")
        
        # Use knowledge base if DuckDuckGo returned no results
        if len(search_results) < request.limit:
            logger.info("Using knowledge base...")
            
            # Find matching keywords - improved matching logic
            # First, try exact or partial matches
            matched_keywords = []
            for keyword in KNOWLEDGE_BASE.keys():
                if keyword.lower() in query_lower or query_lower in keyword.lower():
                    matched_keywords.append(keyword)
            
            # Add results from all matched keywords
            for keyword in matched_keywords:
                if len(search_results) >= request.limit:
                    break
                results = KNOWLEDGE_BASE[keyword]
                for item in results:
                    if len(search_results) >= request.limit:
                        break
                    search_results.append(SearchResult(
                        title=item["title"],
                        link=item["link"],
                        snippet=item["snippet"],
                        source="Knowledge Base"
                    ))
        
        if len(search_results) == 0:
            search_results.append(SearchResult(
                title="No Results Found",
                link="https://www.google.com/search?q=" + request.query.replace(" ", "+"),
                snippet=f"Search '{request.query}' on Google",
                source="Web"
            ))
        
        logger.info(f"✓ Found {len(search_results)} results")
        
        return WebSearchResponse(
            query=request.query,
            results=search_results[:request.limit],
            total_results=len(search_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Web search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/web/test")
async def test_web_search():
    """Test web search endpoint"""
    try:
        request = WebSearchRequest(query="python", num_results=3)
        response = await search_web(request)
        return {
            "status": "✓ OK",
            "message": "Web search is working",
            "results": response.total_results,
            "sample": response.results[0] if response.results else None
        }
    except Exception as e:
        return {
            "status": "✗ Error",
            "message": str(e)
        }
