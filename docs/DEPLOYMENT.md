# 🚀 Hướng dẫn CI/CD và Deployment

## 📋 Mục lục
1. [CI/CD Pipeline](#cicd-pipeline)
2. [Deploy với Docker](#deploy-với-docker)
3. [Deploy lên Heroku](#deploy-lên-heroku)
4. [Deploy lên Railway](#deploy-lên-railway)
5. [Deploy lên VPS](#deploy-lên-vps)

---

## CI/CD Pipeline

### Mô tả
File `ci-cd.yml` trong `.github/workflows/` sẽ **tự động chạy** khi bạn push code lên `main` branch.

**Các bước tự động:**
1. ✅ **Test** - Chạy tests trên Python 3.10, 3.11, 3.12
2. ✅ **Build** - Xây dựng Docker image
3. ✅ **Security Scan** - Quét lỗ hổng bảo mật
4. ✅ **Deploy** - Deploy lên Heroku hoặc Railway (tùy chọn)

### Cách sử dụng
```bash
# 1. Push code lên GitHub
git add .
git commit -m "Update code"
git push origin main

# 2. GitHub Actions sẽ tự động chạy
# 3. Xem kết quả trong tab "Actions" trên GitHub
```

---

## Deploy với Docker

### Chạy local với Docker Compose

```bash
# 1. Build và start
docker-compose up -d

# 2. Mở browser
# Frontend: http://localhost
# API: http://localhost/api
# Docs: http://localhost/docs

# 3. Xem logs
docker-compose logs -f web

# 4. Stop
docker-compose down
```

### Build Docker image riêng

```bash
# Build image
docker build -t translation-app:latest .

# Run container
docker run -d -p 8000:8000 --name translation translation-app:latest

# Stop container
docker stop translation
docker rm translation
```

---

## Deploy lên Heroku

### Bước 1: Tạo Heroku App
```bash
# Cài Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Tạo app
heroku create your-app-name

# Set container
heroku stack:set container
```

### Bước 2: Cấu hình GitHub Secrets
Trên GitHub repo của bạn:
1. Vào **Settings** → **Secrets and variables** → **Actions**
2. Thêm 3 secrets:
   - `HEROKU_API_KEY` - Lấy từ Heroku Account Settings
   - `HEROKU_APP_NAME` - Tên app (ví dụ: `your-app-name`)
   - `HEROKU_EMAIL` - Email Heroku của bạn

### Bước 3: Deploy
```bash
# Push code
git push origin main

# GitHub Actions sẽ tự động deploy
# Xem logs trên Heroku
heroku logs --tail
```

---

## Deploy lên Railway

### Bước 1: Tạo Railway Account
- Vào https://railway.app
- Đăng ký với GitHub

### Bước 2: Tạo Project
1. New Project
2. Deploy from GitHub repo
3. Connect your repository
4. Select branch: `main`

### Bước 3: Cấu hình Environment
Trong Railway project settings:
1. Thêm variable: `PORT=8000`
2. Cấu hình domain nếu cần

### Bước 4: Auto Deploy
Railway sẽ tự động deploy khi bạn push code lên `main` branch.

---

## Deploy lên VPS (SSH)

### Bước 1: Chuẩn bị VPS
```bash
# SSH vào VPS
ssh user@your_vps_ip

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Bước 2: Clone repo
```bash
cd /opt
sudo git clone https://github.com/your-username/Translation.git
cd Translation
```

### Bước 3: Start Application
```bash
# Build và start
sudo docker-compose up -d

# Xem logs
sudo docker-compose logs -f

# Cấu hình Nginx reverse proxy (tùy chọn)
```

### Bước 4: Auto Updates
```bash
# Tạo script auto-update
mkdir -p ~/scripts
cat > ~/scripts/update.sh << 'EOF'
#!/bin/bash
cd /opt/Translation
git pull origin main
docker-compose up -d --build
EOF

chmod +x ~/scripts/update.sh

# Thêm cron job (chạy mỗi giờ)
crontab -e
# Thêm dòng:
# 0 * * * * ~/scripts/update.sh >> ~/scripts/update.log 2>&1
```

---

## 🔐 Environment Variables

### Tạo file `.env`
```bash
# Nếu cần secrets (tùy chọn)
cat > backend/.env << 'EOF'
GOOGLE_TRANSLATE_URL=https://translate.googleapis.com/translate_a/single
DEBUG=false
ENVIRONMENT=production
EOF
```

### Cấu hình cho Docker
Thêm vào `docker-compose.yml`:
```yaml
environment:
  - ENVIRONMENT=production
  - DEBUG=false
```

---

## 📊 Monitoring

### Logs
```bash
# Docker logs
docker-compose logs -f web

# Heroku logs
heroku logs --tail

# Railway logs
railway logs
```

### Health Check
```bash
# Local
curl http://localhost:8000/docs

# Production
curl https://your-domain.com/health
```

---

## 🐛 Troubleshooting

### Docker build fails
```bash
# Clear cache
docker-compose build --no-cache

# Rebuild
docker-compose up -d --build
```

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
lsof -i :8000
kill -9 <PID>
```

### API connection fails
```bash
# Check container
docker ps

# Restart
docker-compose restart web

# Check logs
docker-compose logs web
```

---

## ✅ Checklist Deployment

- [ ] Tất cả tests pass
- [ ] Docker build successful
- [ ] Environment variables configured
- [ ] Health check working
- [ ] Frontend accessible
- [ ] API endpoints responding
- [ ] Security scan passed
- [ ] Logs monitored

---

**Cần giúp? Hãy tạo issue trên GitHub!** 🎉
