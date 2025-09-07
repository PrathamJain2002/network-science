# 🚀 AI-fied Translate AI - Complete Deployment Guide

## 📋 Project Overview

This is a full-stack video translation application that:
- **Frontend**: Node.js/Express server serving static files and handling uploads
- **Backend**: Python FastAPI service for video processing and AI translation
- **Features**: Hindi to Marathi video translation with audio separation and text replacement

## 🎯 Deployment Options

### Option 1: Railway (Recommended for Full-Stack)
Railway is perfect for this project as it supports both Node.js and Python services.

### Option 2: Render
Good alternative with support for both frontend and backend services.

### Option 3: DigitalOcean App Platform
Enterprise-grade deployment with good performance.

### Option 4: AWS/GCP/Azure
For production-scale deployments with custom infrastructure.

---

## 🚂 Railway Deployment (Recommended)

### Step 1: Prepare Your Repository

1. **Create a GitHub repository** and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/video-translation.git
git push -u origin main
```

### Step 2: Set Up Railway

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### Step 3: Configure Services

Railway will detect both services. Configure them as follows:

#### Backend Service (Python/FastAPI)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Port**: Railway will set this automatically

#### Frontend Service (Node.js)
- **Build Command**: `npm install`
- **Start Command**: `node server.js`
- **Port**: Railway will set this automatically

### Step 4: Environment Variables

Set these in Railway dashboard:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key

# Server Configuration
NODE_ENV=production
API_BASE_URL=https://your-backend-service.railway.app
```

### Step 5: Deploy

1. Railway will automatically deploy both services
2. You'll get URLs for both frontend and backend
3. Update the `API_BASE_URL` in frontend environment variables

---

## 🌐 Render Deployment

### Step 1: Backend Service

1. Go to [Render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11

### Step 2: Frontend Service

1. Create another "Web Service"
2. Configure:
   - **Build Command**: `npm install`
   - **Start Command**: `node server.js`
   - **Environment**: Node.js

### Step 3: Environment Variables

Set the same environment variables as Railway, but update `API_BASE_URL` to your Render backend URL.

---

## 🐳 Docker Deployment (Any Platform)

### Step 1: Update Dockerfile

Your current Dockerfile is good, but let's optimize it:

```dockerfile
# Multi-stage build for better optimization
FROM python:3.11-slim as backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install Node.js dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p frames translated_frames separated_audio output audios translated_audio logs bbox uploads

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both services
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port 8000 & node server.js"]
```

### Step 2: Deploy to Any Platform

This Docker setup works on:
- Railway
- Render
- DigitalOcean App Platform
- AWS ECS
- Google Cloud Run
- Azure Container Instances

---

## 🔧 Environment Configuration

### Create .env.example

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Server Configuration
NODE_ENV=production
PORT=3000
API_PORT=8000

# Optional: LALAL.AI for advanced audio separation
LALALAI_API_KEY=your-lalalai-key
```

### Google Cloud Setup

1. **Create a Google Cloud Project**
2. **Enable APIs**:
   - Text-to-Speech API
   - Cloud Translation API (if needed)
3. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Download JSON key
   - Convert JSON to single-line string for `GOOGLE_APPLICATION_CREDENTIALS_JSON`

---

## 📱 Frontend Configuration

### Update server.js for Production

```javascript
// Update the API_BASE_URL to use environment variable
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
```

### Update package.json

```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=8.0.0"
  }
}
```

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-frontend-url.railway.app/health
curl https://your-backend-url.railway.app/health
```

### 2. Upload Test
```bash
curl -X POST -F "video=@test-video.mp4" https://your-frontend-url.railway.app/upload
```

### 3. API Documentation
Visit: `https://your-backend-url.railway.app/docs`

---

## 🚀 Quick Deploy Commands

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render
```bash
# Install Render CLI
npm install -g @render/cli

# Deploy
render deploy
```

### Docker (Any Platform)
```bash
# Build and run locally
docker build -t video-translation .
docker run -p 3000:3000 -p 8000:8000 video-translation

# Push to registry
docker tag video-translation your-registry/video-translation
docker push your-registry/video-translation
```

---

## 📊 Performance Optimization

### 1. Enable Caching
```javascript
// Add to server.js
app.use(express.static('public', {
  maxAge: '1d',
  etag: true
}));
```

### 2. Add Compression
```bash
npm install compression
```

```javascript
const compression = require('compression');
app.use(compression());
```

### 3. Database for Job Management
For production, replace in-memory job storage with:
- PostgreSQL
- MongoDB
- Redis

---

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit API keys to repository
- Use platform-specific secret management
- Rotate keys regularly

### 2. HTTPS
- All platforms provide HTTPS by default
- Use secure headers

### 3. Rate Limiting
```bash
npm install express-rate-limit
```

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use(limiter);
```

---

## 📈 Monitoring & Logs

### 1. Application Logs
- Railway: Built-in logging
- Render: Built-in logging
- Docker: `docker logs container-name`

### 2. Health Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor API response times
- Track error rates

### 3. Performance Metrics
- Monitor CPU and memory usage
- Track video processing times
- Monitor storage usage

---

## 🆘 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python/Node.js versions
   - Verify all dependencies in requirements.txt
   - Check for missing system packages

2. **API Connection Issues**
   - Verify API_BASE_URL environment variable
   - Check CORS settings
   - Ensure both services are running

3. **File Upload Issues**
   - Check file size limits
   - Verify upload directory permissions
   - Check available disk space

4. **Audio Processing Issues**
   - Verify FFmpeg installation
   - Check audio file formats
   - Monitor system resources

### Debug Commands

```bash
# Check service status
curl -f https://your-backend-url/health

# Check logs
railway logs
# or
render logs

# Test API endpoints
curl https://your-backend-url/docs
```

---

## 🎯 Final Checklist

- [ ] Repository is public and accessible
- [ ] Environment variables are set
- [ ] Google Cloud service account is configured
- [ ] OpenAI API key is valid
- [ ] Both services are deployed and healthy
- [ ] Frontend can communicate with backend
- [ ] File uploads work
- [ ] Video processing pipeline works
- [ ] Authentication system works
- [ ] All features are tested

---

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify environment variables
3. Test individual components
4. Check platform-specific documentation
5. Review this deployment guide

Your deployed application should be accessible at the provided URLs and ready for the assignment requirements!
