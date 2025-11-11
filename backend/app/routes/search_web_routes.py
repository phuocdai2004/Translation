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
        {"title": "Python.org Downloads", "link": "https://www.python.org/downloads", "snippet": "Download Python versions. Latest stable release and archives."},
        {"title": "Python Enhancement Proposals", "link": "https://www.python.org/dev/peps", "snippet": "PEP - Python Enhancement Proposals. Standards and design documents."},
        {"title": "PyPI - Python Package Index", "link": "https://pypi.org", "snippet": "PyPI repository for Python packages. pip install packages."},
        {"title": "Python Anaconda", "link": "https://www.anaconda.com", "snippet": "Anaconda distribution for Python. Pre-installed scientific packages."},
        {"title": "Coursera Python Courses", "link": "https://www.coursera.org/search?query=python", "snippet": "Online Python courses from top universities."},
        {"title": "Python Reddit Community", "link": "https://www.reddit.com/r/learnprogramming", "snippet": "r/learnprogramming - Community for learning Python and programming."},
        {"title": "Automate Boring Stuff with Python", "link": "https://automatetheboringstuff.com", "snippet": "Free book and course on practical Python programming."},
        {"title": "DataCamp Python", "link": "https://www.datacamp.com", "snippet": "Interactive Python courses for data science and machine learning."},
        {"title": "Udemy Python Courses", "link": "https://www.udemy.com/courses/search/?q=python", "snippet": "Affordable online Python courses and tutorials."},
        {"title": "GitHub Python Projects", "link": "https://github.com/topics/python", "snippet": "Open source Python projects on GitHub to learn from."},
        {"title": "Python Package Tutorial", "link": "https://python-packaging.readthedocs.io", "snippet": "Guide to creating and packaging Python projects."},
        {"title": "Django - Python Web Framework", "link": "https://www.djangoproject.com", "snippet": "Web framework for Python. Build web applications."},
        {"title": "Flask - Lightweight Framework", "link": "https://flask.palletsprojects.com", "snippet": "Lightweight Python web framework for building web apps."},
        {"title": "Python Type Hints", "link": "https://docs.python.org/3/library/typing.html", "snippet": "Python type hints documentation. Static type checking."},
        {"title": "Python Community Forums", "link": "https://discuss.python.org", "snippet": "Official Python community discussion forums."},
    ],
    "machine learning": [
        {"title": "TensorFlow Official", "link": "https://www.tensorflow.org", "snippet": "Open source ML framework by Google. Build and train ML models easily."},
        {"title": "Scikit-learn", "link": "https://scikit-learn.org", "snippet": "Machine learning library for Python. Classification, regression, clustering and more."},
        {"title": "PyTorch Official", "link": "https://pytorch.org", "snippet": "Deep learning framework. Flexible and powerful for machine learning."},
        {"title": "Kaggle ML Courses", "link": "https://www.kaggle.com/learn", "snippet": "Free machine learning and data science courses on Kaggle."},
        {"title": "Andrew Ng ML Course", "link": "https://www.coursera.org/learn/machine-learning", "snippet": "Comprehensive machine learning course by Andrew Ng on Coursera."},
        {"title": "Fast.ai", "link": "https://www.fast.ai", "snippet": "Practical deep learning course. Top-down learning approach."},
        {"title": "Stanford CS229 ML", "link": "https://cs229.stanford.edu", "snippet": "Stanford's machine learning course. Comprehensive algorithms."},
        {"title": "MIT OpenCourseWare ML", "link": "https://ocw.mit.edu", "snippet": "Free MIT courses on machine learning and AI."},
        {"title": "XGBoost", "link": "https://xgboost.readthedocs.io", "snippet": "Optimized gradient boosting library. For machine learning competitions."},
        {"title": "LightGBM", "link": "https://lightgbm.readthedocs.io", "snippet": "Light gradient boosting machine. Fast training speed."},
        {"title": "OpenAI GPT Models", "link": "https://openai.com/api", "snippet": "Large language models and AI API from OpenAI."},
        {"title": "Hugging Face Models", "link": "https://huggingface.co/models", "snippet": "Hugging Face model hub. Pre-trained transformers and models."},
        {"title": "Papers With Code", "link": "https://paperswithcode.com", "snippet": "ML papers with code implementations and datasets."},
        {"title": "Towards Data Science", "link": "https://towardsdatascience.com", "snippet": "Medium publication for data science and ML articles."},
        {"title": "Machine Learning Mastery", "link": "https://machinelearningmastery.com", "snippet": "Tutorials and guides for machine learning practitioners."},
        {"title": "Colah's Blog", "link": "https://colah.github.io", "snippet": "In-depth blog posts explaining neural networks and deep learning."},
        {"title": "Distill.pub", "link": "https://distill.pub", "snippet": "Interactive articles about machine learning concepts."},
        {"title": "ArXiv ML Papers", "link": "https://arxiv.org/list/stat.ML/recent", "snippet": "Archive of latest ML research papers."},
        {"title": "DeepLearning.AI Courses", "link": "https://www.deeplearning.ai", "snippet": "Courses on deep learning from DeepLearning.AI."},
        {"title": "Coursera ML Specialization", "link": "https://www.coursera.org/specializations/machine-learning", "snippet": "Machine learning specialization with certificates."},
    ],
    "fastapi": [
        {"title": "FastAPI Official", "link": "https://fastapi.tiangolo.com", "snippet": "Modern fast web framework for building APIs with Python 3.7+."},
        {"title": "FastAPI GitHub", "link": "https://github.com/tiangolo/fastapi", "snippet": "FastAPI source code on GitHub. Open source project."},
        {"title": "FastAPI Tutorial", "link": "https://fastapi.tiangolo.com/tutorial", "snippet": "Step-by-step FastAPI tutorial. Learn to build APIs with auto documentation."},
        {"title": "FastAPI Best Practices", "link": "https://fastapi.tiangolo.com/deployment", "snippet": "FastAPI deployment and production best practices guide."},
        {"title": "FastAPI Security", "link": "https://fastapi.tiangolo.com/tutorial/security", "snippet": "Authentication and authorization in FastAPI applications."},
        {"title": "FastAPI CORS", "link": "https://fastapi.tiangolo.com/tutorial/cors", "snippet": "Cross-Origin Resource Sharing configuration in FastAPI."},
        {"title": "FastAPI Database", "link": "https://fastapi.tiangolo.com/advanced/sql-databases", "snippet": "SQL database integration with FastAPI and SQLAlchemy."},
        {"title": "FastAPI Dependency Injection", "link": "https://fastapi.tiangolo.com/tutorial/dependencies", "snippet": "Dependency injection system in FastAPI."},
        {"title": "FastAPI Testing", "link": "https://fastapi.tiangolo.com/tutorial/testing", "snippet": "Unit testing and integration testing in FastAPI."},
        {"title": "Starlette Documentation", "link": "https://www.starlette.io", "snippet": "Starlette ASGI framework. Foundation of FastAPI."},
        {"title": "Pydantic Models", "link": "https://pydantic-docs.helpmanual.io", "snippet": "Data validation library used by FastAPI."},
        {"title": "FastAPI with Docker", "link": "https://fastapi.tiangolo.com/deployment/docker", "snippet": "Containerizing FastAPI applications with Docker."},
        {"title": "FastAPI Performance Tips", "link": "https://fastapi.tiangolo.com/deployment/concepts", "snippet": "Performance optimization and deployment concepts."},
        {"title": "Full Stack FastAPI", "link": "https://github.com/tiangolo/full-stack-fastapi-postgresql", "snippet": "Full stack project template with FastAPI and PostgreSQL."},
        {"title": "FastAPI Examples", "link": "https://github.com/tiangolo/fastapi/tree/master/examples", "snippet": "Example projects and use cases for FastAPI."},
        {"title": "FastAPI WebSockets", "link": "https://fastapi.tiangolo.com/advanced/websockets", "snippet": "WebSocket support in FastAPI for real-time communication."},
        {"title": "FastAPI Async", "link": "https://fastapi.tiangolo.com/async-await", "snippet": "Asynchronous programming with FastAPI."},
        {"title": "FastAPI Background Tasks", "link": "https://fastapi.tiangolo.com/tutorial/background-tasks", "snippet": "Background task execution in FastAPI."},
        {"title": "FastAPI Monitoring", "link": "https://fastapi.tiangolo.com/deployment/concepts", "snippet": "Monitoring and logging FastAPI applications."},
        {"title": "FastAPI Community", "link": "https://github.com/tiangolo/fastapi/discussions", "snippet": "FastAPI community discussions and support."},
    ],
    "lập trình": [
        {"title": "Học Lập Trình Python", "link": "https://www.python.org/", "snippet": "Python là ngôn ngữ lập trình mạnh mẽ, dễ học. Tuyệt vời cho người mới."},
        {"title": "W3Schools Python", "link": "https://www.w3schools.com/python", "snippet": "Hướng dẫn Python từ cơ bản đến nâng cao. Ví dụ minh họa và bài tập."},
        {"title": "Codecademy - Học Lập Trình", "link": "https://www.codecademy.com", "snippet": "Nền tảng học lập trình trực tuyến với các bài tập tương tác."},
        {"title": "freeCodeCamp Tutorials", "link": "https://www.freecodecamp.org", "snippet": "Các video hướng dẫn lập trình miễn phí từ freeCodeCamp."},
        {"title": "GeeksforGeeks", "link": "https://www.geeksforgeeks.org", "snippet": "Nguồn tài liệu lập trình toàn diện với các ví dụ chi tiết."},
        {"title": "GitHub Learn", "link": "https://github.com/learn", "snippet": "Học Git và GitHub. Control version management."},
        {"title": "Udacity Coding Courses", "link": "https://www.udacity.com", "snippet": "Online coding bootcamps và nanodegrees."},
        {"title": "Treehouse Web Development", "link": "https://teamtreehouse.com", "snippet": "Interactive web development and coding courses."},
        {"title": "Pluralsight Courses", "link": "https://www.pluralsight.com", "snippet": "Tech skills platform with thousands of courses."},
        {"title": "Edx Programming", "link": "https://www.edx.org", "snippet": "Free online university courses including programming."},
        {"title": "Linux Academy", "link": "https://linuxacademy.com", "snippet": "Linux and programming training platform."},
        {"title": "Vim Tutorial", "link": "https://www.vim.org", "snippet": "Learning Vim text editor for code editing."},
        {"title": "VS Code Tips", "link": "https://code.visualstudio.com/docs", "snippet": "Visual Studio Code documentation and tips."},
        {"title": "Regex Tutorial", "link": "https://www.regular-expressions.info", "snippet": "Regular expressions for text processing."},
        {"title": "Algorithn Visualizer", "link": "https://algorithm-visualizer.org", "snippet": "Visualize algorithms and data structures."},
        {"title": "Big-O Notation", "link": "https://www.bigocheatsheet.com", "snippet": "Big-O complexity analysis and cheat sheet."},
        {"title": "Design Patterns", "link": "https://refactoring.guru/design-patterns", "snippet": "Software design patterns and principles."},
        {"title": "Clean Code", "link": "https://www.oreilly.com", "snippet": "Best practices for writing clean, maintainable code."},
        {"title": "DevOps Handbook", "link": "https://itrevolution.com/the-devops-handbook", "snippet": "DevOps practices and continuous integration."},
        {"title": "API Design", "link": "https://restfulapi.net", "snippet": "REST API design best practices and conventions."},
    ],
    "dịch thuật": [
        {"title": "Google Translate", "link": "https://translate.google.com", "snippet": "Công cụ dịch thuật miễn phí từ Google. Hỗ trợ 100+ ngôn ngữ."},
        {"title": "DeepL Translator", "link": "https://www.deepl.com/translator", "snippet": "Công cụ dịch thuật AI hiện đại. Chính xác hơn Google Translate."},
        {"title": "Microsoft Translator", "link": "https://www.microsoft.com/en-us/translator", "snippet": "Dịch thuật từ Microsoft. API và công cụ trực tuyến."},
        {"title": "UNESCO - Dịch Thuật Máy", "link": "https://www.un.org", "snippet": "Tài liệu về công nghệ dịch thuật từ UNESCO."},
        {"title": "Machine Translation Evaluation", "link": "https://aclanthology.org", "snippet": "Nghiên cứu và đánh giá công nghệ dịch thuật máy."},
        {"title": "Reverso Context", "link": "https://context.reverso.net", "snippet": "Dịch với ngữ cảnh. Ví dụ thực tế từ các bài phát hành."},
        {"title": "Linguee Dictionary", "link": "https://www.linguee.com", "snippet": "Từ điển dịch thuật với ví dụ thực tế."},
        {"title": "MyMemory Translation", "link": "https://mymemory.translated.net", "snippet": "Cộng đồng dịch thuật. API dịch miễn phí."},
        {"title": "OpenNMT", "link": "https://opennmt.net", "snippet": "Neural machine translation framework mã nguồn mở."},
        {"title": "Tatoeba Corpus", "link": "https://tatoeba.org", "snippet": "Kho ngữ liệu đa ngôn ngữ cho nghiên cứu NLP."},
        {"title": "Babel Fish", "link": "https://www.altavista.com", "snippet": "Công cụ dịch thuật lịch sử từ AltaVista."},
        {"title": "ProZ.com", "link": "https://www.proz.com", "snippet": "Cộng đồng các nhà phiên dịch chuyên nghiệp."},
        {"title": "TranslatorsCafe", "link": "https://www.translatorscafe.com", "snippet": "Diễn đàn và tài nguyên cho biên tập viên."},
        {"title": "Itranslate App", "link": "https://www.itranslate.com", "snippet": "Ứng dụng dịch thuật di động với phiên âm."},
        {"title": "Yandex Translate", "link": "https://translate.yandex.com", "snippet": "Dịch thuật từ Yandex. Hỗ trợ 100+ ngôn ngữ."},
        {"title": "Babylon Translator", "link": "https://www.babylon-software.com", "snippet": "Phần mềm dịch thuật toàn diện."},
        {"title": "Duolingo Language", "link": "https://www.duolingo.com", "snippet": "Học ngôn ngữ mới với Duolingo."},
        {"title": "Memrise", "link": "https://www.memrise.com", "snippet": "Học tập ngôn ngữ qua hình ảnh và âm thanh."},
        {"title": "BBC Learning", "link": "https://www.bbc.co.uk/learning", "snippet": "Tài liệu học tiếng Anh từ BBC."},
        {"title": "Cambridge Dictionary", "link": "https://dictionary.cambridge.org", "snippet": "Từ điển Cambridge với phiên âm âm thanh."},
    ],
    "tài liệu": [
        {"title": "Wikipedia", "link": "https://www.wikipedia.org", "snippet": "Bách khoa toàn thư trực tuyến miễn phí với hàng triệu bài viết."},
        {"title": "Project Gutenberg", "link": "https://www.gutenberg.org", "snippet": "Kho sách điện tử miễn phí với hơn 70,000 cuốn sách."},
        {"title": "Archive.org", "link": "https://archive.org", "snippet": "Kho lưu trữ số kỹ thuật số. Sách, âm thanh, video và hơn thế nữa."},
        {"title": "Google Scholar", "link": "https://scholar.google.com", "snippet": "Công cụ tìm kiếm học thuật cho các bài báo khoa học."},
        {"title": "ResearchGate", "link": "https://www.researchgate.net", "snippet": "Mạng xã hội cho các nhà khoa học và nghiên cứu viên."},
        {"title": "ScienceDirect", "link": "https://www.sciencedirect.com", "snippet": "Kho tài liệu khoa học và các tạp chí học thuật."},
        {"title": "JSTOR", "link": "https://www.jstor.org", "snippet": "Cơ sở dữ liệu tài liệu học thuật và sách."},
        {"title": "PubMed", "link": "https://pubmed.ncbi.nlm.nih.gov", "snippet": "Cơ sở dữ liệu tài liệu y học và sinh học."},
        {"title": "IEEE Xplore", "link": "https://ieeexplore.ieee.org", "snippet": "Tài liệu kỹ thuật điện tử và công nghệp."},
        {"title": "SSRN", "link": "https://www.ssrn.com", "snippet": "Mạng nghiên cứu khoa học xã hội."},
        {"title": "Open Library", "link": "https://openlibrary.org", "snippet": "Kho thư viện mở với hàng triệu sách."},
        {"title": "Scribd Documents", "link": "https://www.scribd.com", "snippet": "Nền tảng chia sẻ tài liệu và sách."},
        {"title": "DocDroid", "link": "https://www.docdroid.net", "snippet": "Chia sẻ và lưu trữ tài liệu trực tuyến."},
        {"title": "SlideShare", "link": "https://www.slideshare.net", "snippet": "Chia sẻ bài thuyết trình và tài liệu."},
        {"title": "Wattpad Stories", "link": "https://www.wattpad.com", "snippet": "Cộng đồng viết lách và chia sẻ câu chuyện."},
        {"title": "Medium Articles", "link": "https://medium.com", "snippet": "Nền tảng xuất bản bài viết và tài liệu."},
        {"title": "Dev.to Articles", "link": "https://dev.to", "snippet": "Cộng đồng lập trình viên chia sẻ bài viết."},
        {"title": "Quora Q&A", "link": "https://www.quora.com", "snippet": "Hỏi và trả lời câu hỏi về nhiều chủ đề."},
        {"title": "Reddit Discussions", "link": "https://www.reddit.com", "snippet": "Cộng đồng thảo luận về hàng ngàn chủ đề."},
        {"title": "HackerNews", "link": "https://news.ycombinator.com", "snippet": "Tin tức công nghệ và thảo luận cho hacker."},
    ],
    "data science": [
        {"title": "Pandas Documentation", "link": "https://pandas.pydata.org", "snippet": "Thư viện phân tích dữ liệu mạnh mẽ cho Python."},
        {"title": "NumPy Official", "link": "https://numpy.org", "snippet": "Thư viện tính toán số cho Python với hiệu suất cao."},
        {"title": "Matplotlib", "link": "https://matplotlib.org", "snippet": "Thư viện vẽ biểu đồ và trực quan hóa dữ liệu cho Python."},
        {"title": "Jupyter Notebook", "link": "https://jupyter.org", "snippet": "Môi trường tương tác cho khoa học dữ liệu và máy tính khoa học."},
        {"title": "Kaggle Datasets", "link": "https://www.kaggle.com/datasets", "snippet": "Kho dữ liệu công khai cho các dự án khoa học dữ liệu."},
        {"title": "Seaborn Visualization", "link": "https://seaborn.pydata.org", "snippet": "Thư viện trực quan hóa dữ liệu thống kê cho Python."},
        {"title": "Plotly", "link": "https://plotly.com/python", "snippet": "Biểu đồ tương tác cho Python và JavaScript."},
        {"title": "SciPy", "link": "https://www.scipy.org", "snippet": "Thư viện khoa học Python. Thống kê, tối ưu hóa, và hơn thế nữa."},
        {"title": "Statsmodels", "link": "https://www.statsmodels.org", "snippet": "Mô hình thống kê và kiểm định giả thuyết cho Python."},
        {"title": "Apache Spark", "link": "https://spark.apache.org", "snippet": "Xử lý dữ liệu lớn phân tán. Big Data processing."},
        {"title": "Hadoop", "link": "https://hadoop.apache.org", "snippet": "Khung công việc xử lý dữ liệu lớn."},
        {"title": "Hadoop MapReduce", "link": "https://hadoop.apache.org/docs/current/hadoop-mapreduce-client", "snippet": "Lập trình MapReduce cho xử lý dữ liệu phân tán."},
        {"title": "Hive SQL", "link": "https://hive.apache.org", "snippet": "Công cụ truy vấn SQL cho Hadoop."},
        {"title": "Pig", "link": "https://pig.apache.org", "snippet": "Nền tảng phân tích dữ liệu cho Hadoop."},
        {"title": "MongoDB", "link": "https://www.mongodb.com", "snippet": "Cơ sở dữ liệu NoSQL cho dữ liệu phi cấu trúc."},
        {"title": "Cassandra Database", "link": "https://cassandra.apache.org", "snippet": "Cơ sở dữ liệu NoSQL phân tán có tính sẵn sàng cao."},
        {"title": "D3.js Visualization", "link": "https://d3js.org", "snippet": "Thư viện JavaScript cho trực quan hóa dữ liệu tương tác."},
        {"title": "Tableau Analytics", "link": "https://www.tableau.com", "snippet": "Nền tảng phân tích dữ liệu và trực quan hóa."},
        {"title": "Power BI", "link": "https://powerbi.microsoft.com", "snippet": "Công cụ phân tích kinh doanh từ Microsoft."},
        {"title": "Google Analytics", "link": "https://analytics.google.com", "snippet": "Phân tích web analytics miễn phí từ Google."},
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
