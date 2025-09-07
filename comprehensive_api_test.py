#!/usr/bin/env python3
"""
Comprehensive API Testing Suite for AI-fied Translate AI
Tests all APIs with real video processing and reduced frame count for speed
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
import logging
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from video_translator import VideoTranslator
from audio_separator import AudioSeparator

def setup_test_logging():
    """Setup comprehensive logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('comprehensive_test.log')
        ]
    )
    return logging.getLogger(__name__)

def create_optimized_test_video(duration=5, filename="comprehensive_test.mp4", fps=15):
    """Create a test video optimized for faster processing"""
    logger = setup_test_logging()
    logger.info(f"🎬 Creating optimized test video: {filename} (duration: {duration}s, fps: {fps})")
    
    try:
        # Create video with lower resolution and frame rate for faster processing
        width, height = 640, 480  # Reduced resolution
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        # Create frames with Hindi text
        for frame_num in range(duration * fps):
            # Create frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame.fill(255)  # White background
            
            # Add Hindi text
            cv2.putText(frame, f"हिंदी पाठ {frame_num}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(frame, f"Frame: {frame_num}", (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Add some visual elements
            cv2.rectangle(frame, (100, 200), (500, 300), (0, 255, 0), 2)
            cv2.circle(frame, (300, 400), 50, (255, 0, 0), -1)
            
            out.write(frame)
        
        out.release()
        
        # Convert to proper MP4 format
        final_filename = filename.replace('.mp4', '_final.mp4')
        cmd = ['ffmpeg', '-i', filename, '-c:v', 'libx264', '-c:a', 'aac', '-y', final_filename]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Clean up temporary file
        if os.path.exists(filename):
            os.remove(filename)
        
        logger.info(f"✅ Optimized test video created: {final_filename}")
        return final_filename
        
    except Exception as e:
        logger.error(f"❌ Failed to create test video: {e}")
        return None

def start_api_server():
    """Start the FastAPI server in background"""
    logger = setup_test_logging()
    logger.info("🚀 Starting FastAPI server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'api:app', 
            '--host', '0.0.0.0', '--port', '8000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                logger.info("✅ FastAPI server started successfully")
                return process
            else:
                logger.error("❌ FastAPI server health check failed")
                return None
        except requests.exceptions.RequestException:
            logger.error("❌ FastAPI server not responding")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start FastAPI server: {e}")
        return None

def start_node_server():
    """Start the Node.js server in background"""
    logger = setup_test_logging()
    logger.info("🚀 Starting Node.js server...")
    
    try:
        # Start server in background
        process = subprocess.Popen(['node', 'server.js'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:3000', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Node.js server started successfully")
                return process
            else:
                logger.error("❌ Node.js server health check failed")
                return None
        except requests.exceptions.RequestException:
            logger.error("❌ Node.js server not responding")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start Node.js server: {e}")
        return None

def test_authentication_apis():
    """Test authentication APIs"""
    logger = setup_test_logging()
    logger.info("🔐 Testing authentication APIs...")
    
    base_url = "http://localhost:8000/api/auth"
    
    try:
        # Test signup
        signup_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/signup", json=signup_data)
        if response.status_code == 201:
            logger.info("✅ User signup successful")
        else:
            logger.info(f"⚠️ Signup response: {response.status_code} - {response.text}")
        
        # Test login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            logger.info("✅ User login successful")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ Protected endpoint access successful: {user_data['username']}")
                return access_token
            else:
                logger.error(f"❌ Protected endpoint failed: {response.status_code}")
                return None
        else:
            logger.error(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        return None

def test_video_upload_api(access_token):
    """Test video upload API"""
    logger = setup_test_logging()
    logger.info("📤 Testing video upload API...")
    
    try:
        # Create test video
        test_video = create_optimized_test_video(duration=3, filename="upload_test.mp4")
        if not test_video:
            logger.error("❌ Failed to create test video for upload")
            return None
        
        # Upload video
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": open(test_video, "rb")}
        
        response = requests.post("http://localhost:8000/upload", 
                               headers=headers, files=files)
        files["file"].close()
        
        if response.status_code == 200:
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            video_id = upload_data.get('video_id')
            logger.info(f"✅ Video upload successful - Job ID: {job_id}")
            return job_id, video_id
        else:
            logger.error(f"❌ Video upload failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Video upload test failed: {e}")
        return None, None

def test_audio_separation_api(job_id, access_token):
    """Test audio separation API"""
    logger = setup_test_logging()
    logger.info("🎵 Testing audio separation API...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test audio separation
        response = requests.post(f"http://localhost:8000/api/separate-audio/{job_id}", 
                               headers=headers)
        
        if response.status_code == 200:
            separation_data = response.json()
            logger.info("✅ Audio separation API successful")
            
            # Test separation quality
            response = requests.get(f"http://localhost:8000/api/audio-separation/{job_id}", 
                                  headers=headers)
            if response.status_code == 200:
                quality_data = response.json()
                logger.info(f"✅ Audio separation quality: {quality_data}")
                return True
            else:
                logger.error(f"❌ Audio separation quality check failed: {response.status_code}")
                return False
        else:
            logger.error(f"❌ Audio separation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Audio separation test failed: {e}")
        return False

def test_translation_apis(job_id, access_token):
    """Test translation APIs"""
    logger = setup_test_logging()
    logger.info("🌐 Testing translation APIs...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test get text translations
        response = requests.get(f"http://localhost:8000/api/translations/{job_id}/text", 
                              headers=headers)
        if response.status_code == 200:
            text_data = response.json()
            logger.info("✅ Get text translations successful")
        else:
            logger.error(f"❌ Get text translations failed: {response.status_code}")
            return False
        
        # Test get audio translation
        response = requests.get(f"http://localhost:8000/api/translations/{job_id}/audio", 
                              headers=headers)
        if response.status_code == 200:
            audio_data = response.json()
            logger.info("✅ Get audio translation successful")
        else:
            logger.error(f"❌ Get audio translation failed: {response.status_code}")
            return False
        
        # Test auto-translate
        response = requests.post(f"http://localhost:8000/api/auto-translate/{job_id}", 
                               headers=headers)
        if response.status_code == 200:
            auto_data = response.json()
            logger.info("✅ Auto-translate successful")
        else:
            logger.error(f"❌ Auto-translate failed: {response.status_code}")
            return False
        
        # Test update text translation
        update_data = {
            "translations": [
                {
                    "id": "test_1",
                    "hindi_text": "हिंदी पाठ",
                    "marathi_text": "मराठी मजकूर",
                    "confidence": 0.95
                }
            ]
        }
        
        response = requests.put(f"http://localhost:8000/api/translations/{job_id}/text", 
                              json=update_data, headers=headers)
        if response.status_code == 200:
            logger.info("✅ Update text translation successful")
        else:
            logger.error(f"❌ Update text translation failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Translation APIs test failed: {e}")
        return False

def test_video_generation_api(job_id, access_token):
    """Test final video generation API"""
    logger = setup_test_logging()
    logger.info("🎬 Testing video generation API...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test generate final video
        response = requests.post(f"http://localhost:8000/api/generate-final-video/{job_id}", 
                               headers=headers)
        
        if response.status_code == 200:
            video_data = response.json()
            logger.info("✅ Final video generation successful")
            return True
        else:
            logger.error(f"❌ Final video generation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Video generation test failed: {e}")
        return False

def test_job_status_api(job_id, access_token):
    """Test job status API"""
    logger = setup_test_logging()
    logger.info("📊 Testing job status API...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test get job status
        response = requests.get(f"http://localhost:8000/status/{job_id}", headers=headers)
        
        if response.status_code == 200:
            status_data = response.json()
            logger.info(f"✅ Job status retrieved: {status_data.get('status')}")
            return True
        else:
            logger.error(f"❌ Job status retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Job status test failed: {e}")
        return False

def test_frontend_endpoints():
    """Test frontend endpoints"""
    logger = setup_test_logging()
    logger.info("🌐 Testing frontend endpoints...")
    
    try:
        # Test main page
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            logger.info("✅ Main page accessible")
        else:
            logger.error(f"❌ Main page failed: {response.status_code}")
            return False
        
        # Test login page
        response = requests.get("http://localhost:3000/login")
        if response.status_code == 200:
            logger.info("✅ Login page accessible")
        else:
            logger.error(f"❌ Login page failed: {response.status_code}")
            return False
        
        # Test signup page
        response = requests.get("http://localhost:3000/signup")
        if response.status_code == 200:
            logger.info("✅ Signup page accessible")
        else:
            logger.error(f"❌ Signup page failed: {response.status_code}")
            return False
        
        # Test editor page
        response = requests.get("http://localhost:3000/editor")
        if response.status_code == 200:
            logger.info("✅ Editor page accessible")
        else:
            logger.error(f"❌ Editor page failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Frontend endpoints test failed: {e}")
        return False

def test_complete_workflow():
    """Test complete workflow with real video processing"""
    logger = setup_test_logging()
    logger.info("🔄 Testing complete workflow...")
    
    try:
        # Create test video
        test_video = create_optimized_test_video(duration=2, filename="workflow_test.mp4")
        if not test_video:
            logger.error("❌ Failed to create test video for workflow")
            return False
        
        # Initialize video translator with test credentials
        translator = VideoTranslator(
            openai_api_key="test-key",  # Will use mock data
            google_credentials_path="sampark-ai-bc13b9af3b55.json",
            font_path="noto-sans-devanagari/NotoSansDevanagari-Regular.ttf"
        )
        
        # Process video (this will use mock data due to test API key)
        result = translator.process_video(
            video_path=test_video,
            video_id="workflow_test_123",
            advanced_ocr=True,
            moving_text=True,
            cleanup=False,  # Don't cleanup for inspection
            test_mode=True  # Use test mode for faster processing
        )
        
        if result:
            logger.info("✅ Complete workflow test successful")
            return True
        else:
            logger.error("❌ Complete workflow test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Complete workflow test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    logger = setup_test_logging()
    logger.info("🧹 Cleaning up test files...")
    
    cleanup_files = [
        "comprehensive_test_final.mp4",
        "upload_test_final.mp4", 
        "workflow_test_final.mp4",
        "comprehensive_test.log"
    ]
    
    cleanup_dirs = [
        "frames/workflow_test_123",
        "translated_frames/workflow_test_123",
        "separated_audio/workflow_test_123",
        "logs/workflow_test_123"
    ]
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"✅ Cleaned up: {file}")
            except:
                pass
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                import shutil
                shutil.rmtree(directory)
                logger.info(f"✅ Cleaned up directory: {directory}")
            except:
                pass

def main():
    """Main comprehensive test function"""
    logger = setup_test_logging()
    logger.info("🚀 Starting Comprehensive API Testing Suite...")
    logger.info("=" * 60)
    
    # Start servers
    api_process = start_api_server()
    node_process = start_node_server()
    
    if not api_process or not node_process:
        logger.error("❌ Failed to start servers")
        return
    
    try:
        test_results = {}
        
        # Test 1: Authentication
        logger.info("\n" + "=" * 60)
        logger.info("🔐 Testing Authentication System")
        logger.info("=" * 60)
        access_token = test_authentication_apis()
        test_results['authentication'] = access_token is not None
        
        if not access_token:
            logger.error("❌ Authentication failed, skipping other tests")
            return
        
        # Test 2: Video Upload
        logger.info("\n" + "=" * 60)
        logger.info("📤 Testing Video Upload")
        logger.info("=" * 60)
        job_id, video_id = test_video_upload_api(access_token)
        test_results['video_upload'] = job_id is not None
        
        if not job_id:
            logger.error("❌ Video upload failed, skipping other tests")
            return
        
        # Test 3: Audio Separation
        logger.info("\n" + "=" * 60)
        logger.info("🎵 Testing Audio Separation")
        logger.info("=" * 60)
        test_results['audio_separation'] = test_audio_separation_api(job_id, access_token)
        
        # Test 4: Translation APIs
        logger.info("\n" + "=" * 60)
        logger.info("🌐 Testing Translation APIs")
        logger.info("=" * 60)
        test_results['translation_apis'] = test_translation_apis(job_id, access_token)
        
        # Test 5: Video Generation
        logger.info("\n" + "=" * 60)
        logger.info("🎬 Testing Video Generation")
        logger.info("=" * 60)
        test_results['video_generation'] = test_video_generation_api(job_id, access_token)
        
        # Test 6: Job Status
        logger.info("\n" + "=" * 60)
        logger.info("📊 Testing Job Status")
        logger.info("=" * 60)
        test_results['job_status'] = test_job_status_api(job_id, access_token)
        
        # Test 7: Frontend Endpoints
        logger.info("\n" + "=" * 60)
        logger.info("🌐 Testing Frontend Endpoints")
        logger.info("=" * 60)
        test_results['frontend_endpoints'] = test_frontend_endpoints()
        
        # Test 8: Complete Workflow
        logger.info("\n" + "=" * 60)
        logger.info("🔄 Testing Complete Workflow")
        logger.info("=" * 60)
        test_results['complete_workflow'] = test_complete_workflow()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed_tests += 1
        
        logger.info(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! The AI-fied Translate AI system is fully functional!")
        else:
            logger.info(f"⚠️ {total_tests - passed_tests} tests failed. Check logs for details.")
        
    finally:
        # Cleanup
        cleanup_test_files()
        
        # Stop servers
        if api_process:
            api_process.terminate()
            logger.info("🛑 FastAPI server stopped")
        
        if node_process:
            node_process.terminate()
            logger.info("🛑 Node.js server stopped")

if __name__ == "__main__":
    main()
