# 🤖 Mô Hình Machine Learning - Nơi Lưu Trữ

## 📍 Tóm Tắt Nhanh

Project sử dụng **3 mô hình ML chính**, được tải từ **Hugging Face Hub** và lưu tại:

| Mô Hình | Chức Năng | Nơi Lưu | Format |
|--------|---------|--------|--------|
| **Helsinki-NLP/opus-mt-en-vi** | Dịch English → Vietnamese | Hugging Face Cache | PyTorch |
| **Helsinki-NLP/opus-mt-vi-en** | Dịch Vietnamese → English | Hugging Face Cache | PyTorch |
| **Sentence-Transformers/all-MiniLM-L6-v2** | Tạo embeddings (semantic search) | Hugging Face Cache | PyTorch |

---

## 🔍 Chi Tiết Về Các Mô Hình

### 1. **Helsinki-NLP/opus-mt-en-vi** - Dịch Anh → Việt

**Thông Tin:**
- Source: Hugging Face Hub
- Task: Machine Translation (EN → VI)
- Framework: Hugging Face Transformers
- Kiến Trúc: Transformer (Seq2Seq)
- Được huấn luyện bởi: Helsinki-NLP

**Kích Thước:**
- Model file: ~300-400 MB
- Download lần đầu: ~500-600 MB
- Ram khi chạy: ~400-500 MB

**Cách Sử Dụng:**
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "Helsinki-NLP/opus-mt-en-vi"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Sử dụng
inputs = tokenizer("Hello world", return_tensors="pt")
outputs = model.generate(**inputs)
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### 2. **Helsinki-NLP/opus-mt-vi-en** - Dịch Việt → Anh

**Thông Tin:**
- Source: Hugging Face Hub
- Task: Machine Translation (VI → EN)
- Framework: Hugging Face Transformers
- Kiến Trúc: Transformer (Seq2Seq)

**Kích Thước:**
- Model file: ~300-400 MB (tương tự mô hình trên)
- Download lần đầu: ~500-600 MB
- Ram khi chạy: ~400-500 MB

### 3. **Sentence-Transformers/all-MiniLM-L6-v2** - Tạo Embeddings

**Thông Tin:**
- Source: Hugging Face Hub
- Task: Semantic Similarity / Embeddings
- Framework: Sentence-Transformers
- Kiến Trúc: BERT-based (6 layers, 22.7M parameters)
- Output: 384 chiều vectors

**Kích Thước:**
- Model file: ~33 MB (nhỏ nhất)
- Download lần đầu: ~60-80 MB
- Ram khi chạy: ~150-200 MB

**Ưu Điểm:**
- Nhanh nhất (MiniLM = Mini Language Model)
- Chính xác cho semantic tasks
- Nhỏ nhất, tối ưu cho inference
- Hỗ trợ 50+ ngôn ngữ

---

## 💾 Nơi Lưu Trữ Các Mô Hình

### **Hugging Face Cache Directory**

Mô hình được lưu tại:

```
Windows:
C:\Users\<USERNAME>\.cache\huggingface\hub\

Linux/Mac:
~/.cache/huggingface/hub/
```

### **Cấu Trúc Thư Mục**

```
C:\Users\<USERNAME>\.cache\huggingface\hub\
├── models--Helsinki-NLP--opus-mt-en-vi/
│   ├── snapshots/
│   │   └── <commit-hash>/
│   │       ├── config.json
│   │       ├── pytorch_model.bin       (model weights)
│   │       ├── tokenizer.json
│   │       ├── source.spm
│   │       └── target.spm
│   └── blobs/
│       └── ... (model files)
│
├── models--Helsinki-NLP--opus-mt-vi-en/
│   └── (tương tự trên)
│
└── models--sentence-transformers--all-MiniLM-L6-v2/
    ├── snapshots/
    │   └── <commit-hash>/
    │       ├── config.json
    │       ├── pytorch_model.bin       (model weights)
    │       ├── sentence_bert_config.json
    │       ├── tokenizer.json
    │       └── modules.json
    └── blobs/
        └── ... (model files)
```

### **Ví Dụ Đường Dẫn Đầy Đủ**

```
C:\Users\PhuocDai\.cache\huggingface\hub\
models--Helsinki-NLP--opus-mt-en-vi\
snapshots\ABC123DEF456\
pytorch_model.bin               (300-400 MB)
```

---

## 🔄 Cách Tải Mô Hình

### **Tải Lần Đầu (Lazy Loading)**

Khi backend khởi động:

```python
# 1. File main.py tìm thấy yêu cầu dịch
# 2. Tự động tải model từ Hugging Face
# 3. Lưu vào cache local (C:\Users\..\.cache\huggingface\hub\)
# 4. Lần tiếp theo dùng từ cache (nhanh hơn)
```

**Tại File:**
- `e:\haystack\backend\app\routes\translation_routes.py`
- `e:\haystack\backend\app\routes\search_routes.py`

```python
def load_translation_models():
    # Auto download từ Hugging Face nếu chưa có
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-vi")
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-vi")
```

### **Embedding Model (Sentence Transformers)**

**Tại File:**
- `e:\haystack\backend\app\services\embedding_service.py` (dòng 45)

```python
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

---

## 📊 Kích Thước Tổng Cộng

| Mô Hình | Download Size | Disk Space | RAM Usage |
|--------|-------------|-----------|-----------|
| Helsinki EN→VI | ~500 MB | ~300 MB | ~400 MB |
| Helsinki VI→EN | ~500 MB | ~300 MB | ~400 MB |
| MiniLM Embeddings | ~60 MB | ~33 MB | ~150 MB |
| **Total** | **~1.1 GB** | **~633 MB** | **~950 MB** |

---

## 🌐 Hugging Face Hub

### Liên Kết Download

1. **Helsinki-NLP OPUS-MT EN-VI**
   ```
   https://huggingface.co/Helsinki-NLP/opus-mt-en-vi
   ```

2. **Helsinki-NLP OPUS-MT VI-EN**
   ```
   https://huggingface.co/Helsinki-NLP/opus-mt-vi-en
   ```

3. **Sentence Transformers MiniLM**
   ```
   https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
   ```

---

## ⚙️ Cấu Hình Trong Project

### **File: `e:\haystack\backend\download_models.py`**

```python
print("Required models:")
print("- Helsinki-NLP/opus-mt-en-vi (English to Vietnamese)")
print("- Helsinki-NLP/opus-mt-vi-en (Vietnamese to English)")
print("- sentence-transformers/all-MiniLM-L6-v2 (Embeddings)")
print("\nModels will be downloaded automatically on first API call.")
```

### **Nơi Sử Dụng**

1. **Translation Route** (`translation_routes.py`)
   ```python
   Helsinki-NLP/opus-mt-en-vi  → /api/translate (EN→VI)
   Helsinki-NLP/opus-mt-vi-en  → /api/translate (VI→EN)
   ```

2. **Embedding Service** (`embedding_service.py`)
   ```python
   sentence-transformers/all-MiniLM-L6-v2 → /api/documents/search
   ```

---

## 🔄 Luồng Tải Mô Hình

### Khi Bạn Dịch Văn Bản

```
1. User gửi request dịch
   ↓
2. Backend check cache (~/.cache/huggingface/)
   ├─ Nếu có → Dùng luôn (nhanh)
   └─ Nếu không → Download từ Hugging Face
   ↓
3. Load model vào RAM
   ↓
4. Dịch text
   ↓
5. Trả về kết quả
```

### Khi Bạn Tìm Kiếm Document

```
1. User nhập query tìm kiếm
   ↓
2. Backend check cache embeddings model
   ├─ Nếu có → Dùng luôn
   └─ Nếu không → Download từ Hugging Face
   ↓
3. Chuyển query thành vector (384 dims)
   ↓
4. Tìm kiếm trong ANNOY index
   ↓
5. Trả về kết quả tương tự
```

---

## 🎯 Giải Thích Chi Tiết

### **Tại Sao Cơ Địa Hugging Face?**

✅ **Miễn phí** - Tất cả mô hình đều open-source
✅ **Đáng tin cậy** - Được sử dụng bởi hàng triệu developer
✅ **Cập nhật thường xuyên** - Luôn có phiên bản mới tốt hơn
✅ **Hỗ trợ tốt** - Community lớn, documentation chi tiết
✅ **Quản lý dễ** - Tự động download, cache locally

### **Tại Sao Những Mô Hình Này?**

| Mô Hình | Lý Do Chọn |
|--------|-----------|
| **Helsinki OPUS-MT** | SOTA (State-of-the-art) cho dịch EN-VI, VI-EN |
| **MiniLM** | Nhỏ, nhanh, chính xác cho semantic search |

---

## 💡 Cách Download Thủ Công

Nếu muốn tải trước mô hình (không đợi khi dùng):

```bash
# Command 1: Download EN→VI
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-vi'); AutoModelForSeq2SeqLM.from_pretrained('Helsinki-NLP/opus-mt-en-vi')"

# Command 2: Download VI→EN  
python -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-vi-en'); AutoModelForSeq2SeqLM.from_pretrained('Helsinki-NLP/opus-mt-vi-en')"

# Command 3: Download Embeddings
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

---

## 📁 Tóm Lược Nơi Lưu

### **Mô Hình (Models)**
```
~/.cache/huggingface/hub/
├── models--Helsinki-NLP--opus-mt-en-vi/
├── models--Helsinki-NLP--opus-mt-vi-en/
└── models--sentence-transformers--all-MiniLM-L6-v2/
```

### **Tokenizers**
```
~/.cache/huggingface/hub/
├── models--Helsinki-NLP--opus-mt-en-vi/
│   └── snapshots/.../tokenizer.json
├── models--Helsinki-NLP--opus-mt-vi-en/
│   └── snapshots/.../tokenizer.json
└── models--sentence-transformers--all-MiniLM-L6-v2/
    └── snapshots/.../tokenizer.json
```

### **Dữ Liệu Khác Của Project**
```
e:\haystack\
├── documents.db              (Dữ liệu document)
├── data/
│   ├── annoy.index          (Vector index)
│   └── doc_mapping.json     (Metadata mapping)
└── backend/
    └── app/
        ├── models/          (Data models - Pydantic, không phải ML models)
        └── services/        (Code dùng ML models)
```

---

## 🎓 Câu Trả Lời Cho Thầy

**Thầy hỏi: "Mô hình nó đâu?"**

**Câu trả lời:**

> Project sử dụng **3 mô hình Machine Learning**:
>
> 1. **Helsinki-NLP/opus-mt-en-vi** - Dịch Anh → Việt
> 2. **Helsinki-NLP/opus-mt-vi-en** - Dịch Việt → Anh  
> 3. **sentence-transformers/all-MiniLM-L6-v2** - Tạo vector embeddings
>
> **Nơi Lưu:**
> - Mô hình được **tải từ Hugging Face Hub** (online) lần đầu
> - Sau đó **lưu vào cache local** tại:
>   - **Windows:** `C:\Users\<USERNAME>\.cache\huggingface\hub\`
>   - **Linux/Mac:** `~/.cache/huggingface/hub\`
> - Tổng dung lượng: **~1.1 GB** (download), **~633 MB** (đĩa)
>
> **Cách Hoạt Động:**
> - Lần đầu dùng: Download từ Hugging Face (~5-10 phút tùy mạng)
> - Lần sau: Dùng từ cache local (nhanh gấp 100 lần)
> - Mô hình tự động load khi cần (lazy loading)
>
> **Loại Mô Hình:**
> - Translation: Transformer-based Seq2Seq (Helsinki-NLP)
> - Embeddings: BERT-based (Sentence Transformers)

---

## 📚 Tài Liệu Thêm

- **Hugging Face Hub:** https://huggingface.co
- **Transformers Library:** https://huggingface.co/docs/transformers
- **Sentence Transformers:** https://www.sbert.net

---

**Status:** ✅ **MÔ HÌNH LƯU TRỮ TẠI HUGGING FACE HUB & LOCAL CACHE**
