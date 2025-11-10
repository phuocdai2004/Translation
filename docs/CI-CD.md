# CI/CD & Deployment Guide

## Overview

This project includes automated CI/CD pipelines using GitHub Actions for testing, building, and deploying the application.

## Workflows

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

Runs on every push and pull request to `main` and `develop` branches.

**Steps:**
- **Test**: Runs Python tests with multiple Python versions (3.10, 3.11)
- **Build**: Builds the application package
- **Deploy**: Deploys to main branch (on push only)

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### 2. Docker Build & Push (`.github/workflows/docker.yml`)

Builds and pushes Docker images to GitHub Container Registry (GHCR).

**Features:**
- Multi-stage Docker builds
- Automatic image tagging (branch, version, SHA)
- Cache optimization

**Triggers:**
```yaml
on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
```

## Local Development with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose (included with Docker Desktop)

### Build and Run Locally

```bash
# Clone repository
git clone https://github.com/phuocdai2004/Translation.git
cd haystack

# Build Docker image
docker build -t translation-app:latest .

# Or use Docker Compose
docker-compose up --build
```

### Access the Application

```
http://localhost:8000
```

### Stop the Application

```bash
# With Docker Compose
docker-compose down

# Or stop Docker container
docker stop translation-app
```

## Deployment Options

### Option 1: Docker Hub

```bash
# Tag image
docker tag translation-app:latest <your-username>/translation-app:latest

# Push to Docker Hub
docker push <your-username>/translation-app:latest

# Pull and run
docker run -p 8000:8000 <your-username>/translation-app:latest
```

### Option 2: GitHub Container Registry (GHCR)

Already configured in `docker.yml` workflow. Images are automatically pushed to:
```
ghcr.io/phuocdai2004/translation:latest
```

Run with:
```bash
docker pull ghcr.io/phuocdai2004/translation:latest
docker run -p 8000:8000 ghcr.io/phuocdai2004/translation:latest
```

### Option 3: Cloud Deployment

#### Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create translation-app

# Push to Heroku
git push heroku main

# View logs
heroku logs --tail
```

#### AWS (with Docker)

```bash
# Push to Amazon ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag translation-app:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/translation-app:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/translation-app:latest
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/translation-app

# Deploy
gcloud run deploy translation-app --image gcr.io/PROJECT-ID/translation-app --platform managed
```

#### Azure Container Instances

```bash
# Build image
az acr build --registry <registry-name> --image translation-app:latest .

# Deploy
az container create --resource-group <group-name> \
  --name translation-app \
  --image <registry>.azurecr.io/translation-app:latest \
  --ports 8000 \
  --dns-name-label translation-app
```

## Environment Variables

Create `.env` file for local development:

```env
# Server configuration
HOST=127.0.0.1
PORT=8000
DEBUG=False

# API settings
MAX_UPLOAD_SIZE=10485760  # 10MB
TIMEOUT=30

# Translation
TRANSLATION_API=google  # google, libretranslate, etc.

# Search
SEARCH_ENGINE=duckduckgo
SEARCH_TIMEOUT=10
```

## Testing

### Run Tests Locally

```bash
# All tests
python -m pytest

# Specific test
python -m pytest test_api.py -v

# With coverage
python -m pytest --cov=backend --cov-report=html
```

### Continuous Testing

Tests automatically run on every commit via GitHub Actions.

## Monitoring & Logging

### Health Check

API includes a health check endpoint:
```bash
curl http://localhost:8000/api/health
```

### Docker Health Status

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Logs

```bash
# Docker Compose logs
docker-compose logs -f web

# Docker container logs
docker logs -f translation-app

# GitHub Actions logs
# View in: GitHub Repository → Actions → Workflow runs
```

## CI/CD Secrets

For GitHub Actions to work with private repositories or external services, configure secrets:

1. Go to: **Repository → Settings → Secrets and variables → Actions**
2. Add secrets:
   - `DOCKER_USERNAME` - Docker Hub username
   - `DOCKER_PASSWORD` - Docker Hub password/token
   - `GH_TOKEN` - GitHub Personal Access Token

## Troubleshooting

### Docker build fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild
docker build --no-cache -t translation-app:latest .
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /F /PID <PID>  # Windows

# Use different port
docker run -p 8001:8000 translation-app:latest
```

### Workflow fails

1. Check GitHub Actions logs: **Repository → Actions**
2. Look for error messages
3. Verify secrets are configured
4. Test locally first: `docker-compose up`

## Best Practices

1. **Use version tags**: `v1.0.0`, `v1.0.1`, etc.
2. **Keep images small**: Use multi-stage builds
3. **Scan for vulnerabilities**: `docker scan translation-app`
4. **Use secrets**: Never commit API keys or passwords
5. **Test before deploying**: Run tests locally
6. **Monitor in production**: Use health checks and logging
7. **Document changes**: Update CHANGELOG
8. **Use environment variables**: For configuration

## Quick Commands

```bash
# Build
docker build -t translation-app:latest .

# Run
docker run -p 8000:8000 translation-app:latest

# Docker Compose
docker-compose up
docker-compose down
docker-compose ps
docker-compose logs -f

# Push to registry
docker push <registry>/translation-app:latest

# Pull from registry
docker pull <registry>/translation-app:latest

# Check health
curl http://localhost:8000/api/health
```

## Related Files

- `.github/workflows/ci-cd.yml` - CI/CD pipeline
- `.github/workflows/docker.yml` - Docker build workflow
- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Docker Compose configuration
- `.dockerignore` - Files to exclude from Docker build

## Support

For issues or questions:
- GitHub Issues: https://github.com/phuocdai2004/Translation/issues
- GitHub Discussions: https://github.com/phuocdai2004/Translation/discussions

---

**Version**: 1.0.0
**Last Updated**: November 11, 2025
