# 📊 SQLite Database - Giải Thích Chi Tiết

## 1. **SQLite là gì?**

SQLite là một **database engine nhẹ, không cần server**. Khác với MySQL/PostgreSQL, SQLite lưu trữ dữ liệu trong **một file duy nhất**.

```
MySQL/PostgreSQL:
  Client → Network → Server (running on port 3306/5432) → Disk

SQLite:
  App → File: documents.db (trực tiếp trên disk)
```

**Ưu điểm SQLite:**
- ✅ Không cần setup server
- ✅ Một file duy nhất (dễ backup, share)
- ✅ Tốc độ nhanh cho read-heavy workloads
- ✅ Không cần database administrator

**Nhược điểm:**
- ❌ Không tốt cho concurrent writes
- ❌ Không scalable (max vài GB)
- ❌ Không clustering/replication

---

## 2. **File Database Vật Lý**

### **Vị trí file:**
```
e:\haystack\backend\documents.db
```

### **Kích thước:**
- **32 KB** (chứa 3 documents + schema)
- Sẽ tăng khi thêm documents + embeddings

### **Mở file bằng gì?**

**Option A: SQLite Browser (GUI)**
- Download: https://sqlitebrowser.org/
- Double-click `documents.db` → xem data bằng giao diện

**Option B: Command line**
```bash
sqlite3 e:\haystack\backend\documents.db
sqlite> .tables                    # Xem tất cả tables
sqlite> SELECT * FROM document;   # Xem tất cả documents
sqlite> .quit                     # Thoát
```

**Option C: Python (trong code)**
```python
import sqlite3
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM document')
for row in cursor.fetchall():
    print(row)
```

---

## 3. **Schema của Database**

```sql
CREATE TABLE document (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT,
  language TEXT,
  embedding BLOB,
  doc_metadata TEXT,  -- JSON format
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Giải thích từng column:**

| Column | Type | Ý nghĩa |
|--------|------|---------|
| `id` | INTEGER PRIMARY KEY | Tự tăng (1, 2, 3, ...) |
| `title` | TEXT | Tên tài liệu (ví dụ: "Python Programming") |
| `content` | TEXT | Nội dung tài liệu (toàn bộ text) |
| `language` | TEXT | Ngôn ngữ ('en', 'vi', etc) |
| `embedding` | BLOB | **Vector 384 chiều** (binary format .npy) |
| `doc_metadata` | TEXT | JSON metadata (author, source, etc) |
| `created_at` | TIMESTAMP | Thời gian tạo (auto-generate) |

---

## 4. **Dữ Liệu Hiện Tại (Ví dụ)**

```
┌────┬──────────────────────┬────────┬──────────────┬─────────────┐
│ ID │ Title                │ Lang   │ Content Size │ Embedding   │
├────┼──────────────────────┼────────┼──────────────┼─────────────┤
│ 1  │ Python Programming   │ en     │ 250 bytes    │ 1544 bytes  │
│ 2  │ Machine Learning B.. │ en     │ 280 bytes    │ 1544 bytes  │
│ 3  │ Web Development      │ en     │ 220 bytes    │ 1544 bytes  │
└────┴──────────────────────┴────────┴──────────────┴─────────────┘
```

### **Mỗi embedding:**
- **Size:** 384 floats × 4 bytes = ~1544 bytes
- **Format:** Binary numpy (.npy)
- **Mục đích:** Dùng cho semantic search

---

## 5. **Mối Quan Hệ: Database ↔ Backend ↔ Frontend**

```
┌──────────────┐
│  Frontend    │ (HTML + JavaScript)
│  (Browser)   │
└──────┬───────┘
       │ HTTP Request
       │ POST /api/documents/upload
       │ {title: "...", content: "..."}
       ▼
┌──────────────────────┐
│     Backend          │ (FastAPI + Python)
│  (app.py)            │
│                      │
│  1. Generate         │
│     embedding        │ sentence-transformers
│                      │
│  2. Serialize to     │ numpy → bytes
│     BLOB             │
│                      │
│  3. Insert to DB     │ INSERT INTO document ...
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ documents.db (SQLite)│  ← **File vật lý**
│                      │
│ [Table: document]    │
│ id | title | emb...  │
└──────────────────────┘
```

---

## 6. **Query Ví Dụ**

### **Thêm document:**
```sql
INSERT INTO document (title, content, language, embedding, created_at)
VALUES (
  'Python Programming',
  'Python is a high-level programming...',
  'en',
  X'0123456789ABCDEF...',  -- Binary embedding
  '2025-11-14 10:30:00'
);
```

### **Xem tất cả documents:**
```sql
SELECT id, title, language FROM document;
```

### **Tìm kiếm theo title:**
```sql
SELECT * FROM document WHERE title LIKE '%Python%';
```

### **Xóa document:**
```sql
DELETE FROM document WHERE id = 1;
```

---

## 7. **Kết Nối Database ↔ Semantic Search**

### **Quy trình Upload:**
```
1. User upload file "machine_learning.pdf"
   ↓
2. Backend parse → extract text
   ↓
3. Generate embedding (384-dim vector)
   ↓
4. Serialize embedding → binary (BLOB)
   ↓
5. INSERT INTO document (title, content, embedding, ...)
   ↓
6. Database lưu
   ↓
7. Thêm vào Annoy index (data/annoy.index)
```

### **Quy trình Search:**
```
1. User search: "machine learning algorithms"
   ↓
2. Generate embedding cho query
   ↓
3. Query Annoy index → tìm top-3 vectors gần nhất
   ↓
4. SELECT * FROM document WHERE id IN (...)
   ↓
5. Return documents + similarity scores
```

---

## 8. **Production vs Development**

### **Development (Hiện tại):**
```
SQLite (documents.db)
├─ Pros: Đơn giản, không cần setup
├─ Cons: Không scalable, chậm với writes
└─ Phù hợp: Prototype, demo, learning
```

### **Production (Tương lai):**
```
PostgreSQL + pgvector
├─ Pros: Scalable, fast, native vector support
├─ Cons: Phức tạp hơn, cần admin
└─ Phù hợp: Real-world deployment
```

**Migration Plan:**
```
1. Develop trên SQLite
2. Test trên PostgreSQL locally
3. Deploy PostgreSQL trên cloud (AWS RDS)
4. Sử dụng pgvector extension cho vector search
```

---

## 9. **Cách Xem & Quản Lý Database**

### **Cách 1: Python (trong code)**
```python
import sqlite3

# Connect
conn = sqlite3.connect('backend/documents.db')
cursor = conn.cursor()

# Query
cursor.execute('SELECT * FROM document')
for row in cursor.fetchall():
    print(row)

# Close
conn.close()
```

### **Cách 2: SQLite CLI**
```bash
cd backend
sqlite3 documents.db
sqlite> .schema              # Xem schema
sqlite> SELECT COUNT(*) FROM document;  # Đếm documents
sqlite> .quit
```

### **Cách 3: GUI - SQLite Browser**
- Download: https://sqlitebrowser.org/
- Open: File → Open Database → chọn `documents.db`
- Browse dữ liệu bằng giao diện

---

## 10. **Lưu Ý Quan Trọng**

### **⚠️ BLOB (Binary Large Object)**
- `embedding` column lưu binary data (vector)
- Không thể xem trực tiếp như text
- Khi SELECT, phải deserialize từ binary → numpy array

### **⚠️ Concurrent Access**
- SQLite không tốt khi multiple processes write cùng lúc
- Nếu có >1 API worker, cần PostgreSQL

### **⚠️ File Lock**
- SQLite lock cả file khi write
- Nếu API crash, file có thể lock → restart cần chmod

---

## 11. **Troubleshooting**

**Q: Database file bị corrupt?**
```bash
sqlite3 documents.db "PRAGMA integrity_check;"
```

**Q: Database file quá lớn?**
```bash
sqlite3 documents.db "VACUUM;"  # Compress database
```

**Q: Xóa tất cả data?**
```bash
sqlite3 documents.db "DELETE FROM document; VACUUM;"
```

---

## 📝 **Summary**

| Khía cạnh | Chi tiết |
|----------|---------|
| **File** | `backend/documents.db` (32 KB) |
| **Type** | SQLite (serverless database) |
| **Table** | `document` (7 columns) |
| **Data** | 3 sample documents + embeddings |
| **Query** | SQL via Python sqlite3 module |
| **Scaling** | SQLite (dev) → PostgreSQL (prod) |
| **Embedding** | Lưu dưới dạng BLOB (binary) |
| **Search** | Query DB + Annoy index |

---

**Khi thầy hỏi "Database ở đâu?":**
- Trả lời: `backend/documents.db` (file vật lý)
- Mở file: Dùng SQLite Browser hoặc Python
- Schema: 7 columns, including BLOB embedding

✅ **Ready để trình bày!** 🚀
