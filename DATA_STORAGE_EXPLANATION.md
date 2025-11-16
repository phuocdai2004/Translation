# 💾 Nơi Lưu Trữ Dữ Liệu

## 📍 Tóm Tắt Nhanh

Dữ liệu trong project của bạn được lưu ở **3 nơi**:

| Nơi Lưu | Loại Dữ Liệu | Vị Trí |
|---------|-------------|--------|
| **SQLite Database** | Thông tin tài liệu, nội dung | `e:\haystack\documents.db` hoặc `e:\haystack\backend\documents.db` |
| **Vector Index** | Embeddings (Vector embedding) | `e:\haystack\data\annoy.index` |
| **Metadata Mapping** | Ánh xạ tài liệu | `e:\haystack\data\doc_mapping.json` |

---

## 🗄️ Chi Tiết 1: Database SQLite (documents.db)

### Vị Trí File
```
e:\haystack\documents.db
e:\haystack\backend\documents.db
```

### Cấu Trúc Database

**Bảng: `document`**

| Cột | Kiểu Dữ Liệu | Mô Tả |
|-----|-------------|--------|
| `id` | INTEGER | ID tài liệu (auto-increment, PRIMARY KEY) |
| `title` | VARCHAR(255) | Tiêu đề tài liệu |
| `content` | TEXT | Nội dung đầy đủ của tài liệu |
| `language` | VARCHAR(50) | Ngôn ngữ (VN hoặc EN) |
| `doc_metadata` | JSON | Metadata bổ sung (JSON format) |
| `embedding` | BLOB | Vector embedding (dạng binary) |
| `created_at` | DATETIME | Thời gian tạo |

### Indexes (Chỉ Mục Tìm Kiếm)
```sql
-- Tìm kiếm nhanh theo ngôn ngữ
CREATE INDEX idx_document_language ON document(language)

-- Tìm kiếm nhanh theo tiêu đề
CREATE INDEX idx_document_title ON document(title)

-- Tìm kiếm nhanh theo ngày tạo
CREATE INDEX idx_document_created_at ON document(created_at)
```

### Ví Dụ Dữ Liệu Trong Database

```
ID: 1
Title: "Tiếng Anh Giao Tiếp"
Content: "English is a global language used for..."
Language: "en"
Created At: 2025-11-16 10:30:45
Embedding: [0x45F3A2B1E4D2...]  (Binary vector)
```

---

## 🤖 Chi Tiết 2: Vector Index (annoy.index)

### Vị Trí File
```
e:\haystack\data\annoy.index
```

### Chức Năng
- Lưu trữ **vector embeddings** từ Sentence Transformers
- Dùng thuật toán **ANNOY** (Approximate Nearest Neighbors On Yahoo!)
- Dùng cho **semantic search** (tìm kiếm ngữ nghĩa)

### Kích Thước Vector
- Mỗi document được chuyển thành vector **384 chiều**
- Format: Binary (compact, nhanh)

### Ví Dụ
```
Document: "Ngôn ngữ là công cụ giao tiếp"
         ↓ (Sentence Transformers Model)
Vector: [0.234, -0.567, 0.123, ..., 0.456]  (384 chiều)
         ↓ (Lưu vào ANNOY Index)
annoy.index: [Binary data]
```

---

## 📋 Chi Tiết 3: Metadata Mapping (doc_mapping.json)

### Vị Trí File
```
e:\haystack\data\doc_mapping.json
```

### Nội Dung
JSON file ánh xạ ID trong vector index với ID trong database

### Ví Dụ nội dung
```json
{
  "0": "1",
  "1": "2",
  "2": "3",
  "index_id": "db_id"
}
```

**Ý nghĩa:**
- Key (0, 1, 2...): ID trong vector index (ANNOY)
- Value ("1", "2", "3"...): ID tương ứng trong database SQLite

---

## 🔄 Luồng Lưu Trữ Dữ Liệu

### Khi Upload Document

```
1. Bạn upload tài liệu
   ↓
2. Lưu vào DATABASE (SQLite)
   - Title, Content, Language, Timestamp
   ↓
3. Chuyển thành VECTOR (Sentence Transformers)
   - 384 chiều embeddings
   ↓
4. Lưu VECTOR vào INDEX (ANNOY)
   - Tối ưu hóa cho tìm kiếm
   ↓
5. Cập nhật MAPPING (doc_mapping.json)
   - Liên kết index_id ↔ db_id
```

### Khi Search Document

```
1. Bạn nhập query tìm kiếm
   ↓
2. Chuyển query thành VECTOR
   - Cùng mô hình Sentence Transformers
   ↓
3. Tìm kiếm trong ANNOY INDEX
   - Tìm k vectors gần nhất
   ↓
4. Lấy mapping từ doc_mapping.json
   - index_id → db_id
   ↓
5. Truy vấn DATABASE để lấy thông tin
   - SELECT * FROM document WHERE id = db_id
   ↓
6. Trả về kết quả cho user
```

---

## 📊 Cấu Trúc Thư Mục

```
e:\haystack\
├── documents.db                    ← SQLite Database (Copy ở root)
├── data/
│   ├── annoy.index                ← Vector Index
│   └── doc_mapping.json           ← Metadata Mapping
├── backend/
│   ├── documents.db               ← SQLite Database (Copy ở backend)
│   ├── data/
│   │   ├── annoy.index
│   │   └── doc_mapping.json
│   └── app/
│       ├── database.py            ← Quản lý database
│       ├── models/                ← Database models
│       └── services/
│           └── document_service.py ← Xử lý document
```

---

## 🔍 Cách Xem Dữ Liệu

### 1. Xem SQLite Database

**Dùng SQL**
```sql
SELECT * FROM document;
```

**Hoặc dùng tool:**
- DB Browser for SQLite
- DBeaver
- VS Code Extension: SQLite

### 2. Xem Vector Index

Không thể xem trực tiếp (binary format)
Nhưng có thể xem thông qua API:

```python
# Trong backend code
index.get_nns_by_item(0)  # Lấy 10 neighbors gần nhất của item 0
```

### 3. Xem Metadata Mapping

```bash
cat e:\haystack\data\doc_mapping.json
```

Hoặc mở bằng text editor

---

## 💡 Giải Thích Chi Tiết

### Tại Sao Phải Có 3 Loại Lưu Trữ?

| Loại | Lý Do |
|------|-------|
| **SQLite Database** | Lưu toàn bộ thông tin gốc (title, content, metadata) dễ dàng truy vấn, backup |
| **Vector Index** | Tối ưu hóa tìm kiếm semantic (tìm kiếm giống nghĩa) nhanh 100 lần so với tìm kiếm text |
| **Metadata Mapping** | Liên kết giữa 2 hệ thống trên để không mất dữ liệu khi cập nhật |

### Lợi Ích

✅ **Nhanh:** ANNOY index cho tìm kiếm O(log n)
✅ **Chính xác:** Semantic search thay vì keyword search
✅ **An toàn:** Có backup trong SQLite
✅ **Flexible:** Dễ thêm/xóa tài liệu

---

## 🛡️ Backup & Bảo Vệ Dữ Liệu

### Những File Cần Backup

```
e:\haystack\documents.db          ← CẬP CẬP THƯỜNG XUYÊN
e:\haystack\data\annoy.index      ← CẬP CẬP KHI CÓ TÀI LIỆU MỚI
e:\haystack\data\doc_mapping.json ← CẬP CẬP KHI CÓ TÀI LIỆU MỚI
```

### Cách Backup
```bash
# Copy các file quan trọng
copy e:\haystack\documents.db C:\backup\
copy e:\haystack\data\ C:\backup\data\ /s /y
```

---

## 📈 Kích Thước Dữ Liệu

### Ước Tính

| Loại | Kích Thước/Document |
|------|------------------|
| SQLite (1 document) | ~1-5 KB (tùy nội dung) |
| Vector Index (1 document) | ~1.5 KB (384 floats) |
| Total (1 document) | ~2.5-6.5 KB |

### Ví Dụ: 1000 tài liệu
```
SQLite: ~5 MB
Vectors: ~1.5 MB
Mapping: ~50 KB
Total: ~6.5 MB
```

---

## 🔧 Cấu Hình Database

### File: `e:\haystack\backend\app\database.py`

```python
# Database URL
DB_FILE = os.environ.get("APP_DB", "documents.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

# Có thể đổi sang:
# - PostgreSQL: postgresql://user:pass@localhost/dbname
# - MySQL: mysql+pymysql://user:pass@localhost/dbname
# - SQLServer: mssql+pyodbc://user:pass@localhost/dbname
```

### Để Đổi Database

1. **Đổi environment variable:**
```bash
set APP_DB=custom_db.db
```

2. **Hoặc sửa trực tiếp file:**
```python
DB_FILE = "my_database.db"  # Thay đổi tên
```

---

## 🎯 Câu Trả Lời Cho Thầy

**Thầy hỏi: "Dữ liệu nó lưu ở đâu?"**

**Câu trả lời:**

> Dữ liệu được lưu ở **3 nơi**:
>
> 1. **SQLite Database** (`documents.db`) - Lưu thông tin tài liệu (tiêu đề, nội dung, ngôn ngữ)
> 2. **Vector Index** (`data/annoy.index`) - Lưu vector embeddings để tìm kiếm ngữ nghĩa
> 3. **Metadata Mapping** (`data/doc_mapping.json`) - Liên kết giữa 2 hệ thống trên
>
> Khi upload tài liệu, nó được:
> - Lưu nội dung vào **SQLite** (dễ truy vấn)
> - Chuyển thành **vector** (384 chiều) bằng Sentence Transformers
> - Lưu vector vào **ANNOY Index** (tìm kiếm nhanh)
> - Ánh xạ ID trong `doc_mapping.json`
>
> Khi tìm kiếm, hệ thống:
> - Chuyển query thành vector
> - Tìm vectors gần nhất trong ANNOY Index
> - Lấy dữ liệu gốc từ SQLite
> - Trả về kết quả cho user

---

## 📚 Tài Liệu Thêm

- **SQLAlchemy**: ORM framework (database layer)
- **ANNOY**: Approximate Nearest Neighbors library
- **Sentence Transformers**: NLP model để chuyển text → vectors

---

**Status**: ✅ **DỮ LIỆU ĐƯỢC LƯU AN TOÀN VÀ CÓ CẤU TRÚC TỐT**
