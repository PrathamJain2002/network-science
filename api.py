#!/usr/bin/env python3
"""
FastAPI Video Translation Service

Asynchronously processes Hindi video translation to Marathi
and returns the output video path.
"""

import asyncio
import os
import uuid
import shutil
from datetime import datetime
from typing import Dict, Optional
import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, validator
import uvicorn

from video_translator import translate_video
from audio_separator import AudioSeparator
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta

# Initialize FastAPI app
app = FastAPI(
    title="Video Translation API",
    description="Translate Hindi videos to Marathi with text and audio translation",
    version="1.0.0"
)

# In-memory storage for job status (in production, use Redis or database)
job_status: Dict[str, Dict] = {}

# In-memory storage for users (in production, use a proper database)
users_db: Dict[str, Dict] = {}

# JWT secret key (in production, use environment variable)
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def ensure_api_directories():
    """Ensure all necessary directories exist for the API"""
    directories = [
        "frames",
        "translated_frames",
        "output",
        "temp",
        "logs",
        "bbox",
        "audios",
        "translated_audio"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Ensured directory exists: {directory}/")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize directories and resources on startup"""
    print("🚀 Starting Video Translation API...")
    ensure_api_directories()
    print("✅ API initialization complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🔄 Shutting down Video Translation API...")
    print("✅ Shutdown complete")

# Request/Response models
class VideoTranslationRequest(BaseModel):
    video_path: str
    font_path: Optional[str] = "noto-sans-devanagari/NotoSansDevanagari-Regular.ttf"
    cleanup: Optional[bool] = True
    env_file: Optional[str] = ".env"
    job_id: Optional[str] = None  # Optional custom job ID for consistent naming
    moving_text: Optional[bool] = False  # Whether video contains moving text
    advanced_ocr: Optional[bool] = True  # Whether to use advanced OCR with preprocessing
    
    @validator('video_path')
    def validate_video_path(cls, v):
        if not v or not v.strip():
            raise ValueError("video_path cannot be empty")
        return v.strip()

class VideoTranslationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    video_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[str] = None
    video_path: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


def update_job_status(job_id: str, status: str, **kwargs):
    """Update job status in memory"""
    if job_id in job_status:
        job_status[job_id].update({
            'status': status,
            **kwargs
        })


def ensure_job_directories(job_id: str):
    """Ensure job-specific directories exist"""
    job_dirs = [
        f"frames/{job_id}",
        f"translated_frames/{job_id}",
        f"temp/{job_id}",
        f"logs/{job_id}"
    ]
    
    for directory in job_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"❌ Error creating job directory {directory}: {e}")
            return False
    return True


async def process_video_async(job_id: str, request: VideoTranslationRequest):
    """
    Asynchronously process video translation
    """
    try:
        # Ensure job directories exist
        if not ensure_job_directories(job_id):
            raise Exception("Failed to create job directories")
        
        # Update status to processing
        update_job_status(job_id, "processing", progress="Starting video translation...")
        
        # Run the translate_video function in a thread pool
        # Since translate_video is CPU-intensive, we run it in an executor
        loop = asyncio.get_event_loop()
        
        # Update progress
        update_job_status(job_id, "processing", progress="Extracting frames...")
        
        # Execute the translation in thread pool to avoid blocking
        output_video_path = await loop.run_in_executor(
            None,  # Use default thread pool
            lambda: translate_video(
                video_path=request.video_path,
                font_path=request.font_path,
                cleanup=request.cleanup,
                env_file=request.env_file,
                video_id=job_id,  # Use job_id as video_id for consistent naming
                moving_text=request.moving_text,  # Pass moving text flag
                advanced_ocr=request.advanced_ocr  # Pass advanced OCR flag
            )
        )
        
        # Move output video to output directory if it's not already there
        output_dir = "output"
        if not output_video_path.startswith(output_dir):
            final_output_path = os.path.join(output_dir, os.path.basename(output_video_path))
            try:
                shutil.move(output_video_path, final_output_path)
                output_video_path = final_output_path
            except Exception as e:
                print(f"Warning: Could not move output video to output directory: {e}")
        
        # Update status to completed
        update_job_status(
            job_id, 
            "completed", 
            video_path=output_video_path,
            completed_at=datetime.utcnow(),
            progress="Translation completed successfully!"
        )
        
        print(f"✅ Job {job_id} completed successfully: {output_video_path}")
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {str(e)}"
        update_job_status(
            job_id, 
            "failed", 
            error=error_msg,
            completed_at=datetime.utcnow()
        )
        print(f"❌ Job {job_id} failed: {error_msg}")
        
    except ValueError as e:
        error_msg = f"Configuration error: {str(e)}"
        update_job_status(
            job_id, 
            "failed", 
            error=error_msg,
            completed_at=datetime.utcnow()
        )
        print(f"❌ Job {job_id} failed: {error_msg}")
        
    except Exception as e:
        error_msg = f"Translation failed: {str(e)}"
        traceback.print_exc()  # Log full traceback
        update_job_status(
            job_id, 
            "failed", 
            error=error_msg,
            completed_at=datetime.utcnow()
        )
        print(f"❌ Job {job_id} failed: {error_msg}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Video Translation API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.post("/api/auth/signup")
async def signup(request: dict):
    """User signup endpoint"""
    try:
        full_name = request.get("fullName")
        email = request.get("email")
        password = request.get("password")
        confirm_password = request.get("confirmPassword")
        
        # Validate inputs
        if not all([full_name, email, password, confirm_password]):
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Check if user already exists
        if email in users_db:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create user
        user_id = secrets.token_hex(16)
        hashed_password = hash_password(password)
        
        users_db[email] = {
            "id": user_id,
            "fullName": full_name,
            "email": email,
            "password": hashed_password,
            "createdAt": datetime.utcnow().isoformat(),
            "isActive": True
        }
        
        return {
            "success": True,
            "message": "User created successfully",
            "userId": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


@app.post("/api/auth/login")
async def login(request: dict):
    """User login endpoint"""
    try:
        email = request.get("email")
        password = request.get("password")
        remember_me = request.get("rememberMe", False)
        
        # Validate inputs
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")
        
        # Check if user exists
        if email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = users_db[email]
        
        # Verify password
        if not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if user is active
        if not user.get("isActive", True):
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Create access token
        expires_delta = timedelta(days=30) if remember_me else timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": user["id"], "email": email},
            expires_delta=expires_delta
        )
        
        # Update last login
        user["lastLogin"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "message": "Login successful",
            "token": access_token,
            "user": {
                "id": user["id"],
                "fullName": user["fullName"],
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/api/auth/me")
async def get_current_user(request: dict):
    """Get current user information"""
    try:
        # In a real implementation, this would extract the token from the Authorization header
        # For now, we'll use a simple approach
        token = request.get("token")
        
        if not token:
            raise HTTPException(status_code=401, detail="Token is required")
        
        # Verify token
        payload = verify_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        if email not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users_db[email]
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "fullName": user["fullName"],
                "email": user["email"],
                "createdAt": user["createdAt"],
                "lastLogin": user.get("lastLogin")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Check if .env file exists
    env_exists = os.path.exists(".env")
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "env_file_exists": env_exists,
        "active_jobs": len([j for j in job_status.values() if j['status'] == 'processing'])
    }


@app.get("/api/translations/{job_id}/text")
async def get_text_translations(job_id: str):
    """Get text translations for a job"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would load from database
        # For now, return mock data
        mock_translations = [
            {
                "id": 1,
                "hindiText": "छल्ला चुंबक",
                "marathiText": "वलयाकार चुंबक",
                "confidence": 0.95,
                "bbox": [100, 200, 300, 250]
            },
            {
                "id": 2,
                "hindiText": "छड़ चुंबक",
                "marathiText": "दंड चुंबक",
                "confidence": 0.92,
                "bbox": [100, 300, 300, 350]
            }
        ]
        
        return {
            "success": True,
            "translations": mock_translations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get text translations: {str(e)}")


@app.get("/api/translations/{job_id}/audio")
async def get_audio_translation(job_id: str):
    """Get audio translation for a job"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would load from database
        # For now, return mock data
        mock_audio_data = {
            "hindiTranscription": "छल्ला चुंबक आणि छड़ चुंबक यांच्या गुणधर्मांचा अभ्यास करूया",
            "marathiTranslation": "वलयाकार चुंबक आणि दंड चुंबक यांच्या गुणधर्मांचा अभ्यास करूया"
        }
        
        return {
            "success": True,
            **mock_audio_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audio translation: {str(e)}")


@app.put("/api/translations/{job_id}/text")
async def update_text_translations(job_id: str, request: dict):
    """Update text translations for a job"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        translations = request.get("translations", [])
        
        # In a real implementation, this would save to database
        # For now, just return success
        
        return {
            "success": True,
            "message": "Text translations updated successfully",
            "updated_count": len(translations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update text translations: {str(e)}")


@app.put("/api/translations/{job_id}/audio")
async def update_audio_translation(job_id: str, request: dict):
    """Update audio translation for a job"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        marathi_translation = request.get("marathiTranslation", "")
        
        # In a real implementation, this would save to database
        # For now, just return success
        
        return {
            "success": True,
            "message": "Audio translation updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update audio translation: {str(e)}")


@app.post("/api/auto-translate/{job_id}")
async def auto_translate_text(job_id: str):
    """Auto-translate all text using AI"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would use OpenAI API
        # For now, return mock data
        mock_translations = [
            {
                "id": 1,
                "hindiText": "छल्ला चुंबक",
                "marathiText": "वलयाकार चुंबक",
                "confidence": 0.95,
                "bbox": [100, 200, 300, 250]
            },
            {
                "id": 2,
                "hindiText": "छड़ चुंबक",
                "marathiText": "दंड चुंबक",
                "confidence": 0.92,
                "bbox": [100, 300, 300, 350]
            }
        ]
        
        return {
            "success": True,
            "message": "Auto-translation completed successfully",
            "translations": mock_translations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-translation failed: {str(e)}")


@app.post("/api/regenerate-translation/{job_id}/{translation_id}")
async def regenerate_translation(job_id: str, translation_id: int):
    """Regenerate a specific translation using AI"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would use OpenAI API
        # For now, return mock data
        mock_translation = "वलयाकार चुंबक"  # Mock Marathi translation
        
        return {
            "success": True,
            "message": "Translation regenerated successfully",
            "marathiText": mock_translation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate translation: {str(e)}")


@app.post("/api/regenerate-audio/{job_id}")
async def regenerate_audio(job_id: str, request: dict):
    """Regenerate Marathi audio with updated translation"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        marathi_text = request.get("marathiText", "")
        
        # In a real implementation, this would use Google TTS
        # For now, just return success
        
        return {
            "success": True,
            "message": "Audio regenerated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate audio: {str(e)}")


@app.get("/api/audio-separation/{job_id}")
async def get_audio_separation_info(job_id: str):
    """Get audio separation quality information"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would load from database
        # For now, return mock data
        mock_quality = {
            "voiceQuality": 85.2,
            "musicQuality": 78.5,
            "overallQuality": 82.1
        }
        
        return {
            "success": True,
            "qualityMetrics": mock_quality
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audio separation info: {str(e)}")


@app.post("/api/reseparate-audio/{job_id}")
async def reseparate_audio(job_id: str):
    """Re-separate audio with improved quality"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would use the AudioSeparator
        # For now, return mock data
        mock_quality = {
            "voiceQuality": 88.5,
            "musicQuality": 82.3,
            "overallQuality": 85.4
        }
        
        return {
            "success": True,
            "message": "Audio re-separation completed successfully",
            "qualityMetrics": mock_quality
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-separate audio: {str(e)}")


@app.post("/api/generate-final-video/{job_id}")
async def generate_final_video(job_id: str):
    """Generate final video with all edits applied"""
    try:
        if job_id not in job_status:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # In a real implementation, this would trigger the final video generation
        # For now, just return success
        
        return {
            "success": True,
            "message": "Final video generated successfully",
            "videoPath": f"output/output_{job_id}.mp4"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate final video: {str(e)}")


@app.post("/separate-audio")
async def separate_audio_endpoint(request: dict):
    """
    Separate audio into voice and background music tracks
    
    Request body:
    {
        "audio_path": "path/to/audio.wav",
        "output_dir": "path/to/output" (optional),
        "method": "custom" (optional, default: "custom")
    }
    """
    try:
        audio_path = request.get("audio_path")
        output_dir = request.get("output_dir", "separated_audio")
        method = request.get("method", "custom")
        
        if not audio_path:
            raise HTTPException(status_code=400, detail="audio_path is required")
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail=f"Audio file not found: {audio_path}")
        
        # Initialize audio separator
        separator = AudioSeparator(method=method)
        
        # Perform separation
        result = separator.separate_audio(audio_path, output_dir)
        
        # Get quality metrics
        quality = separator.get_separation_quality(
            audio_path, result['voice'], result['music']
        )
        
        return {
            "success": True,
            "voice_track": result['voice'],
            "music_track": result['music'],
            "quality_metrics": quality,
            "message": "Audio separation completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio separation failed: {str(e)}")


@app.post("/translate", response_model=VideoTranslationResponse)
async def translate_video_async(
    request: VideoTranslationRequest, 
    background_tasks: BackgroundTasks
):
    """
    Start asynchronous video translation
    
    Returns immediately with a job_id for tracking progress.
    """
    # Validate video file exists
    if not os.path.exists(request.video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found: {request.video_path}"
        )
    
    # Validate .env file exists
    if not os.path.exists(request.env_file):
        raise HTTPException(
            status_code=400,
            detail=f"Environment file not found: {request.env_file}. Please create .env file with your credentials."
        )
    
    # Use provided job ID or generate unique job ID
    job_id = request.job_id if request.job_id else str(uuid.uuid4())
    
    # Validate job_id is not already in use
    if job_id in job_status:
        raise HTTPException(
            status_code=409,
            detail=f"Job ID {job_id} is already in use. Please use a different job_id or omit it to auto-generate."
        )
    
    # Initialize job status
    start_time = datetime.utcnow()
    job_status[job_id] = {
        'job_id': job_id,
        'status': 'queued',
        'progress': 'Job queued for processing',
        'video_path': None,
        'started_at': start_time,
        'completed_at': None,
        'error': None,
        'request': request.dict()
    }
    
    # Start background processing
    background_tasks.add_task(process_video_async, job_id, request)
    
    return VideoTranslationResponse(
        job_id=job_id,
        status="queued",
        message="Video translation job started. Use /status/{job_id} to track progress.",
        started_at=start_time
    )


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a video translation job
    """
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job_data = job_status[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job_data['status'],
        progress=job_data.get('progress'),
        video_path=job_data.get('video_path'),
        started_at=job_data['started_at'],
        completed_at=job_data.get('completed_at'),
        error=job_data.get('error')
    )


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download the translated video file
    """
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job_data = job_status[job_id]
    
    if job_data['status'] != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed. Status: {job_data['status']}"
        )
    
    video_path = job_data.get('video_path')
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found for job {job_id}"
        )
    
    return FileResponse(
        path=video_path,
        filename=f"translated_{job_id}.mp4",
        media_type="video/mp4"
    )


@app.get("/jobs")
async def list_jobs():
    """
    List all jobs and their statuses
    """
    return {
        "total_jobs": len(job_status),
        "jobs": [
            {
                "job_id": job_id,
                "status": data['status'],
                "started_at": data['started_at'],
                "completed_at": data.get('completed_at'),
                "video_path": data.get('video_path')
            }
            for job_id, data in job_status.items()
        ]
    }


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its associated files
    """
    if job_id not in job_status:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    job_data = job_status[job_id]
    
    # Delete video file if it exists
    video_path = job_data.get('video_path')
    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Warning: Could not delete video file {video_path}: {e}")
    
    # Remove from job status
    del job_status[job_id]
    
    return {"message": f"Job {job_id} deleted successfully"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    # Check for .env file on startup
    if not os.path.exists(".env"):
        print("❌ Warning: .env file not found!")
        print("Please create .env file with your credentials:")
        print("  cp .env.example .env")
        print("  # Edit .env with your actual API keys")
        print()
    
    # Run the API server
    print("🚀 Starting Video Translation API Server...")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("📊 Health Check: http://localhost:8001/health")
    print()
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )
