# 🚀 Step-by-Step Deployment Guide

## 📋 Prerequisites Checklist

Before we start, make sure you have:
- [ ] GitHub account
- [ ] OpenAI API key
- [ ] Google Cloud account
- [ ] A test video file (MP4 format)

---

## 🎯 Step 1: Prepare Your Code

### 1.1 Check Your Current Files
```bash
# Make sure you're in the project directory
cd "D:\Pratham\Translate AI\video-translation"

# Check if all files are present
ls -la
```

You should see these key files:
- `server.js` (Node.js frontend)
- `api.py` (Python FastAPI backend)
- `requirements.txt` (Python dependencies)
- `package.json` (Node.js dependencies)
- `Dockerfile` (Docker configuration)

### 1.2 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - ready for deployment"
```

---

## 🔑 Step 2: Set Up API Keys

### 2.1 Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### 2.2 Set Up Google Cloud
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable "Cloud Text-to-Speech API":
   - Go to "APIs & Services" → "Library"
   - Search for "Text-to-Speech API"
   - Click "Enable"
4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Name it "video-translation"
   - Download JSON key file
   - Save as `credentials.json` in your project folder

### 2.3 Create Environment File
```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file with your API keys
notepad .env  # On Windows
# or
nano .env     # On Linux/Mac
```

Fill in your `.env` file:
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
JWT_SECRET_KEY=your-super-secret-jwt-key-12345
NODE_ENV=production
PORT=3000
API_PORT=8000
API_BASE_URL=http://localhost:8000
```

---

## 🐙 Step 3: Push to GitHub

### 3.1 Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `video-translation`
4. Make it **Public** (required for free deployment)
5. Don't initialize with README (you already have files)
6. Click "Create repository"

### 3.2 Push Your Code
```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/video-translation.git

# Push your code
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

---

## 🚂 Step 4: Deploy to Railway (Recommended)

### 4.1 Sign Up for Railway
1. Go to [Railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub

### 4.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Find and select your `video-translation` repository
4. Click "Deploy Now"

### 4.3 Configure Services
Railway will automatically detect both services:

**Backend Service (Python):**
- Build Command: `pip install -r requirements.txt`
- Start Command: `python -m uvicorn api:app --host 0.0.0.0 --port $PORT`

**Frontend Service (Node.js):**
- Build Command: `npm install`
- Start Command: `node server.js`

### 4.4 Set Environment Variables
1. Click on your **Backend service**
2. Go to "Variables" tab
3. Add these variables:

```
OPENAI_API_KEY = sk-your-actual-openai-key-here
GOOGLE_APPLICATION_CREDENTIALS_JSON = {"type":"service_account","project_id":"your-project",...}
JWT_SECRET_KEY = your-super-secret-jwt-key-12345
```

For `GOOGLE_APPLICATION_CREDENTIALS_JSON`, you need to:
1. Open your `credentials.json` file
2. Copy the entire content
3. Paste it as a single line (remove all line breaks)
4. Put it in the Railway environment variable

4. Click on your **Frontend service**
5. Go to "Variables" tab
6. Add this variable:

```
API_BASE_URL = https://your-backend-service.railway.app
```

Replace `your-backend-service` with the actual backend URL from Railway.

### 4.5 Wait for Deployment
- Railway will build and deploy both services
- This takes 5-10 minutes
- You'll see build logs in real-time

---

## 🧪 Step 5: Test Your Deployment

### 5.1 Get Your URLs
After deployment, Railway will give you:
- Frontend URL: `https://your-frontend.railway.app`
- Backend URL: `https://your-backend.railway.app`

### 5.2 Test Health Endpoints
```bash
# Test frontend
curl https://your-frontend.railway.app/health

# Test backend
curl https://your-backend.railway.app/health
```

Both should return `{"status":"healthy"}`

### 5.3 Test API Documentation
Visit: `https://your-backend.railway.app/docs`

You should see the FastAPI documentation page.

### 5.4 Test Video Upload
1. Go to your frontend URL: `https://your-frontend.railway.app`
2. You should see the upload page
3. Try uploading a test video file
4. Check if the upload starts successfully

---

## 🔧 Step 6: Troubleshooting

### Common Issues and Solutions:

**Issue 1: Build Fails**
```bash
# Check the build logs in Railway
# Common causes:
# - Missing dependencies in requirements.txt
# - Python/Node.js version issues
```

**Issue 2: Services Can't Connect**
```bash
# Check environment variables
# Make sure API_BASE_URL is set correctly in frontend
# Verify all API keys are correct
```

**Issue 3: File Upload Fails**
```bash
# Check file size (max 100MB)
# Verify file format (MP4, AVI, MOV supported)
# Check upload directory permissions
```

**Issue 4: Google Cloud Errors**
```bash
# Verify service account JSON is correct
# Check if Text-to-Speech API is enabled
# Ensure JSON is properly formatted (single line)
```

---

## 📱 Step 7: Final Testing

### 7.1 Complete Workflow Test
1. **Upload Video**: Upload a Hindi video with embedded text
2. **Check Processing**: Monitor the translation progress
3. **Download Result**: Download the translated Marathi video
4. **Verify Quality**: Check if text and audio are properly translated

### 7.2 Feature Testing Checklist
- [ ] User registration works
- [ ] User login works
- [ ] Video upload works
- [ ] Audio separation works
- [ ] Text extraction works
- [ ] Translation works
- [ ] Video reconstruction works
- [ ] Download works

---

## 🎉 Step 8: You're Live!

### 8.1 Share Your Deployment
Your working application is now live at:
- **Frontend**: `https://your-frontend.railway.app`
- **Backend**: `https://your-backend.railway.app`
- **API Docs**: `https://your-backend.railway.app/docs`

### 8.2 Assignment Submission
For your assignment, provide:
1. **Deployed Link**: Your frontend URL
2. **Source Code**: Your GitHub repository URL
3. **Setup Instructions**: This guide
4. **Demo Video**: Screen recording of the working application

---

## 🆘 Need Help?

### Quick Commands:
```bash
# Check deployment status
railway status

# View logs
railway logs

# Redeploy
railway up
```

### Support Resources:
- Railway Documentation: https://docs.railway.app
- GitHub Issues: Create issue in your repository
- Check build logs in Railway dashboard

---

## 🎯 Success Criteria

Your deployment is successful when:
✅ Frontend loads without errors
✅ Backend API responds to health checks
✅ Video upload works
✅ Translation pipeline processes videos
✅ Users can download translated videos
✅ All assignment requirements are met

**Congratulations! Your AI-fied Translate AI is now live! 🚀**
