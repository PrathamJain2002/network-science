#!/usr/bin/env python3
"""
Manual API Test for AI-fied Translate AI
Run this when servers are already running on localhost:8000 and localhost:3000
"""

import os
import sys
import time
import json
import requests
import logging
from pathlib import Path

def setup_test_logging():
    """Setup logging without emojis for Windows compatibility"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('manual_api_test.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def test_server_connectivity():
    """Test if servers are running"""
    logger = setup_test_logging()
    logger.info("Testing server connectivity...")
    
    try:
        # Test FastAPI server
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            logger.info("FastAPI server is running")
            api_running = True
        else:
            logger.error(f"FastAPI server health check failed: {response.status_code}")
            api_running = False
    except requests.exceptions.RequestException:
        logger.error("FastAPI server is not running")
        api_running = False
    
    try:
        # Test Node.js server
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            logger.info("Node.js server is running")
            node_running = True
        else:
            logger.error(f"Node.js server failed: {response.status_code}")
            node_running = False
    except requests.exceptions.RequestException:
        logger.error("Node.js server is not running")
        node_running = False
    
    return api_running, node_running

def test_authentication():
    """Test authentication APIs"""
    logger = setup_test_logging()
    logger.info("Testing authentication...")
    
    base_url = "http://localhost:8000/api/auth"
    
    try:
        # Test signup
        signup_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/signup", json=signup_data)
        logger.info(f"Signup response: {response.status_code}")
        
        # Test login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            logger.info("Login successful")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Protected endpoint access successful: {user_data['username']}")
                return access_token
            else:
                logger.error(f"Protected endpoint failed: {response.status_code}")
                return None
        else:
            logger.error(f"Login failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Authentication test failed: {e}")
        return None

def test_video_upload(access_token):
    """Test video upload"""
    logger = setup_test_logging()
    logger.info("Testing video upload...")
    
    try:
        # Create a simple test video file
        test_video_path = "test_upload.mp4"
        
        # Create a minimal MP4 file for testing
        import subprocess
        cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=2:size=320x240:rate=1', '-y', test_video_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Upload video
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": open(test_video_path, "rb")}
        
        response = requests.post("http://localhost:8000/upload", 
                               headers=headers, files=files)
        files["file"].close()
        
        logger.info(f"Upload response: {response.status_code}")
        if response.status_code == 200:
            upload_data = response.json()
            job_id = upload_data.get('job_id')
            video_id = upload_data.get('video_id')
            logger.info(f"Upload successful - Job ID: {job_id}")
            return job_id, video_id
        else:
            logger.error(f"Upload failed: {response.text}")
            return None, None
            
    except Exception as e:
        logger.error(f"Video upload test failed: {e}")
        return None, None

def test_translation_apis(job_id, access_token):
    """Test translation APIs"""
    logger = setup_test_logging()
    logger.info("Testing translation APIs...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test get text translations
        response = requests.get(f"http://localhost:8000/api/translations/{job_id}/text", 
                              headers=headers)
        logger.info(f"Get text translations: {response.status_code}")
        
        # Test get audio translation
        response = requests.get(f"http://localhost:8000/api/translations/{job_id}/audio", 
                              headers=headers)
        logger.info(f"Get audio translation: {response.status_code}")
        
        # Test auto-translate
        response = requests.post(f"http://localhost:8000/api/auto-translate/{job_id}", 
                               headers=headers)
        logger.info(f"Auto-translate: {response.status_code}")
        
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
        logger.info(f"Update text translation: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Translation APIs test failed: {e}")
        return False

def test_audio_separation_apis(job_id, access_token):
    """Test audio separation APIs"""
    logger = setup_test_logging()
    logger.info("Testing audio separation APIs...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test audio separation
        response = requests.post(f"http://localhost:8000/api/separate-audio/{job_id}", 
                               headers=headers)
        logger.info(f"Audio separation: {response.status_code}")
        
        # Test separation quality
        response = requests.get(f"http://localhost:8000/api/audio-separation/{job_id}", 
                              headers=headers)
        logger.info(f"Audio separation quality: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Audio separation APIs test failed: {e}")
        return False

def test_video_generation_apis(job_id, access_token):
    """Test video generation APIs"""
    logger = setup_test_logging()
    logger.info("Testing video generation APIs...")
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test generate final video
        response = requests.post(f"http://localhost:8000/api/generate-final-video/{job_id}", 
                               headers=headers)
        logger.info(f"Generate final video: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Video generation APIs test failed: {e}")
        return False

def test_frontend_pages():
    """Test frontend pages"""
    logger = setup_test_logging()
    logger.info("Testing frontend pages...")
    
    pages = [
        ("/", "Main page"),
        ("/login", "Login page"),
        ("/signup", "Signup page"),
        ("/editor", "Editor page")
    ]
    
    all_passed = True
    
    for path, name in pages:
        try:
            response = requests.get(f"http://localhost:3000{path}", timeout=5)
            if response.status_code == 200:
                logger.info(f"{name}: OK")
            else:
                logger.error(f"{name}: Failed ({response.status_code})")
                all_passed = False
        except requests.exceptions.RequestException as e:
            logger.error(f"{name}: Failed ({e})")
            all_passed = False
    
    return all_passed

def cleanup_test_files():
    """Clean up test files"""
    cleanup_files = ["test_upload.mp4", "manual_api_test.log"]
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass

def main():
    """Main test function"""
    logger = setup_test_logging()
    logger.info("Starting Manual API Test...")
    logger.info("=" * 60)
    
    # Test server connectivity
    api_running, node_running = test_server_connectivity()
    
    if not api_running:
        logger.error("FastAPI server is not running. Please start it with: python -m uvicorn api:app --host 0.0.0.0 --port 8000")
        return False
    
    if not node_running:
        logger.error("Node.js server is not running. Please start it with: node server.js")
        return False
    
    test_results = {}
    
    # Test authentication
    logger.info("\n" + "=" * 60)
    logger.info("Testing Authentication")
    logger.info("=" * 60)
    access_token = test_authentication()
    test_results['authentication'] = access_token is not None
    
    if not access_token:
        logger.error("Authentication failed, skipping other tests")
        return False
    
    # Test video upload
    logger.info("\n" + "=" * 60)
    logger.info("Testing Video Upload")
    logger.info("=" * 60)
    job_id, video_id = test_video_upload(access_token)
    test_results['video_upload'] = job_id is not None
    
    if not job_id:
        logger.error("Video upload failed, skipping other tests")
        return False
    
    # Test translation APIs
    logger.info("\n" + "=" * 60)
    logger.info("Testing Translation APIs")
    logger.info("=" * 60)
    test_results['translation_apis'] = test_translation_apis(job_id, access_token)
    
    # Test audio separation APIs
    logger.info("\n" + "=" * 60)
    logger.info("Testing Audio Separation APIs")
    logger.info("=" * 60)
    test_results['audio_separation_apis'] = test_audio_separation_apis(job_id, access_token)
    
    # Test video generation APIs
    logger.info("\n" + "=" * 60)
    logger.info("Testing Video Generation APIs")
    logger.info("=" * 60)
    test_results['video_generation_apis'] = test_video_generation_apis(job_id, access_token)
    
    # Test frontend pages
    logger.info("\n" + "=" * 60)
    logger.info("Testing Frontend Pages")
    logger.info("=" * 60)
    test_results['frontend_pages'] = test_frontend_pages()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed_tests += 1
    
    logger.info(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("ALL TESTS PASSED! The AI-fied Translate AI APIs are working correctly!")
    else:
        logger.info(f"{total_tests - passed_tests} tests failed. Check logs for details.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
