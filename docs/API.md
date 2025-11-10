# Machine Translation & Document Search API Documentation

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### Translation Endpoints

#### POST /translate
Translate text from source language to target language.

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "vi"
}
```

**Response:**
```json
{
  "original_text": "Hello, how are you?",
  "translated_text": "Xin chào, bạn khỏe không?",
  "source_lang": "en",
  "target_lang": "vi",
  "confidence": 0.95
}
```

**Status Codes:**
- `200`: Translation successful
- `400`: Invalid request
- `500`: Server error

---

#### GET /translate/languages
Get list of supported language pairs.

**Response:**
```json
{
  "supported_pairs": [
    {
      "from": "en",
      "to": "vi",
      "name": "English to Vietnamese"
    },
    {
      "from": "vi",
      "to": "en",
      "name": "Vietnamese to English"
    }
  ],
  "total": 2
}
```

---

### Document Endpoints

#### POST /documents/upload
Upload and index a new document.

**Request Body:**
```json
{
  "title": "Sample Document",
  "content": "This is the document content...",
  "language": "en",
  "metadata": {
    "author": "John Doe",
    "date": "2024-01-01"
  }
}
```

**Response:**
```json
{
  "doc_id": "doc_1",
  "title": "Sample Document",
  "status": "indexed",
  "message": "Document successfully uploaded and indexed"
}
```

---

#### GET /documents/list
List all uploaded documents.

**Response:**
```json
{
  "documents": [
    {
      "doc_id": "doc_1",
      "title": "Sample Document",
      "language": "en"
    }
  ],
  "total": 1
}
```

---

#### GET /documents/{doc_id}
Get a specific document by ID.

**Response:**
```json
{
  "doc_id": "doc_1",
  "title": "Sample Document",
  "content": "This is the document content...",
  "language": "en",
  "metadata": {}
}
```

---

#### DELETE /documents/{doc_id}
Delete a document.

**Response:**
```json
{
  "status": "deleted",
  "doc_id": "doc_1",
  "message": "Document successfully deleted"
}
```

---

### Search Endpoints

#### POST /search
Search documents using semantic similarity.

**Request Body:**
```json
{
  "query": "machine learning",
  "top_k": 5,
  "language": "en"
}
```

**Response:**
```json
{
  "query": "machine learning",
  "results": [
    {
      "doc_id": "doc_1",
      "title": "Sample Document",
      "content": "Content snippet...",
      "score": 0.92
    }
  ],
  "total_results": 1,
  "processing_time": 0.123
}
```

---

#### GET /search/stats
Get search statistics.

**Response:**
```json
{
  "total_documents": 5,
  "indexed": true,
  "last_updated": "2024-01-01T00:00:00Z"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error codes:
- `400`: Bad Request - Invalid input data
- `404`: Not Found - Document or resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server-side error

---

## Rate Limiting

Currently, there are no rate limits. However, large documents or batch requests may take longer to process.

---

## Examples

### Example 1: Translate and Search

```bash
# 1. Translate text
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Machine learning is amazing",
    "source_lang": "en",
    "target_lang": "vi"
  }'

# 2. Upload a document
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ML Article",
    "content": "Machine learning is the field...",
    "language": "en"
  }'

# 3. Search documents
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "top_k": 5,
    "language": "en"
  }'
```

---

## Notes

- Maximum text length for translation: 5000 characters
- Search results are scored from 0 to 1 (1 being most relevant)
- Documents are indexed automatically upon upload
- Metadata is optional for document uploads
