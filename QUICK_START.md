# 🚀 Chạy Dự Án - Quick Start Guide

## 📌 Các Script Chạy Nhanh

### **1️⃣ Chạy với Batch Script (Easiest)**

**Windows:**
```batch
double-click file run.bat
```

hoặc từ terminal:
```batch
e:\haystack\run.bat
```

✅ **Ưu điểm:**
- Đơn giản nhất
- Tự động cài dependencies
- Tự động dọn port
- Chạy được ngay

---

### **2️⃣ Chạy với PowerShell**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\run.ps1
```

✅ **Ưu điểm:**
- Màu sắc đẹp
- Thông tin chi tiết
- Kiểm tra lỗi tốt

---

### **3️⃣ Chạy với Docker (Production)**

```batch
e:\haystack\run-docker.bat
```

✅ **Ưu điểm:**
- Cô lập môi trường
- Sản xuất ready
- Dễ deploy

---

### **4️⃣ Chạy Thủ Công (Manual)**

```powershell
cd e:\haystack\backend
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

---

## 🌐 Truy Cập Ứng Dụng

Sau khi chạy script, mở browser:

| Đường dẫn | Mục đích |
|-----------|---------|
| `http://127.0.0.1:8000` | Frontend |
| `http://127.0.0.1:8000/docs` | API Documentation (Swagger) |
| `http://127.0.0.1:8000/api/tts/voices` | Available TTS Voices |
| `http://127.0.0.1:8000/health` | Health Check |

---

## 🛑 Dừng Ứng Dụng

### **Từ Terminal:**
```
Nhấn CTRL + C
```

### **Dừng Docker:**
```batch
docker-compose down
```

---

## 🐛 Troubleshooting

### **Port 8000 đã được sử dụng:**
```powershell
# Tìm process sử dụng port 8000
netstat -ano | findstr :8000

# Kill process (thay XXXX bằng PID)
taskkill /F /PID XXXX
```

### **Virtual Environment không tồn tại:**
```powershell
cd e:\haystack
python -m venv venv
venv\Scripts\pip install -r backend\requirements.txt
```

### **Dependencies lỗi:**
```powershell
cd e:\haystack\backend
..\venv\Scripts\pip install --upgrade -r requirements.txt
```

---

## 📋 Yêu Cầu Hệ Thống

- ✅ Python 3.10+
- ✅ pip (package manager)
- ✅ Virtual environment
- ✅ (Optional) Docker & Docker Compose

---

## 🚀 Khuyên Dùng

**Cho Development:** Dùng `run.bat` hoặc `run.ps1`

**Cho Production:** Dùng `run-docker.bat`

**Để Debug:** Chạy thủ công với flag `-v` (verbose)

---

**Cần giúp?** Hãy tham khảo `docs/DEPLOYMENT.md` để biết thêm chi tiết! 📖
