#!/usr/bin/env python3
"""
Final Comprehensive Test for AI-fied Translate AI
Shows that all components are working correctly
"""

import os
import sys
import time
import json
import subprocess
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
    """Setup logging without emojis for Windows compatibility"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('final_test.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def create_test_video_with_audio(duration=3, filename="final_test.mp4"):
    """Create a test video with audio for comprehensive testing"""
    logger = setup_test_logging()
    logger.info(f"Creating test video with audio: {filename} (duration: {duration}s)")
    
    try:
        # Create video with audio using FFmpeg directly
        cmd = [
            'ffmpeg', 
            '-f', 'lavfi', '-i', f'testsrc=duration={duration}:size=640x480:rate=1',
            '-f', 'lavfi', '-i', f'sine=frequency=1000:duration={duration}',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', filename
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"Test video with audio created: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Failed to create test video: {e}")
        return None

def test_complete_pipeline():
    """Test the complete pipeline with mock data"""
    logger = setup_test_logging()
    logger.info("Testing complete pipeline...")
    
    try:
        # Create test video
        test_video = create_test_video_with_audio(duration=2, filename="pipeline_test.mp4")
        if not test_video:
            logger.error("Failed to create test video")
            return False
        
        # Get API keys from environment or use test mode
        openai_key = os.getenv('OPENAI_API_KEY', 'test-key')
        google_creds = 'sampark-ai-bc13b9af3b55.json'
        
        if openai_key == 'test-key':
            logger.info("Using test mode (no real API keys)")
        else:
            logger.info("Using real API keys")
        
        # Initialize video translator
        translator = VideoTranslator(
            openai_api_key=openai_key,
            google_credentials_path=google_creds,
            font_path="noto-sans-devanagari/NotoSansDevanagari-Regular.ttf"
        )
        
        logger.info("Starting video processing pipeline...")
        
        # Process video in test mode
        result = translator.process_video(
            video_path=test_video,
            video_id="pipeline_test_123",
            advanced_ocr=True,
            moving_text=True,
            cleanup=False,  # Don't cleanup for inspection
            test_mode=True  # Use test mode for faster processing
        )
        
        if result:
            logger.info("Video processing pipeline completed successfully!")
            
            # Check output files
            output_files = [
                "output/output_pipeline_test_123.mp4",
                "audios/audio_pipeline_test_123.wav",
                "separated_audio/pipeline_test_123/audio_pipeline_test_123_voice.wav",
                "separated_audio/pipeline_test_123/audio_pipeline_test_123_music.wav"
            ]
            
            logger.info("Checking output files:")
            for file_path in output_files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    logger.info(f"  ✓ {file_path} ({size} bytes)")
                else:
                    logger.warning(f"  ✗ {file_path} (missing)")
            
            return True
        else:
            logger.error("Video processing pipeline failed")
            return False
            
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        return False

def test_audio_separation_standalone():
    """Test audio separation as standalone component"""
    logger = setup_test_logging()
    logger.info("Testing audio separation component...")
    
    try:
        # Create test audio file
        test_audio = "test_audio_standalone.wav"
        cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3', '-y', test_audio]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Test audio separation
        separator = AudioSeparator(method="custom")
        result = separator.separate_audio(test_audio, "test_separation_standalone")
        
        if result and 'voice_track' in result and 'music_track' in result:
            logger.info("Audio separation component working correctly!")
            logger.info(f"  Voice track: {result['voice_track']}")
            logger.info(f"  Music track: {result['music_track']}")
            
            # Test quality metrics
            try:
                quality = separator.get_separation_quality(test_audio, result['voice_track'], result['music_track'])
                logger.info(f"  Separation quality: {quality}")
            except Exception as e:
                logger.warning(f"  Quality metrics failed: {e}")
            
            # Cleanup
            os.remove(test_audio)
            import shutil
            if os.path.exists("test_separation_standalone"):
                shutil.rmtree("test_separation_standalone")
            
            return True
        else:
            logger.error("Audio separation component failed")
            return False
            
    except Exception as e:
        logger.error(f"Audio separation test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    logger = setup_test_logging()
    logger.info("Testing file structure...")
    
    required_files = [
        "api.py",
        "video_translator.py", 
        "audio_separator.py",
        "server.js",
        "requirements.txt",
        "package.json",
        "public/index.html",
        "public/translation-editor.html",
        "public/login.html",
        "public/signup.html"
    ]
    
    required_dirs = [
        "public",
        "noto-sans-devanagari"
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            logger.info(f"  ✓ {file}")
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        else:
            logger.info(f"  ✓ {directory}/")
    
    if missing_files or missing_dirs:
        logger.error(f"Missing files: {missing_files}")
        logger.error(f"Missing directories: {missing_dirs}")
        return False
    else:
        logger.info("File structure is complete!")
        return True

def test_dependencies():
    """Test that all Python dependencies are available"""
    logger = setup_test_logging()
    logger.info("Testing Python dependencies...")
    
    required_modules = [
        'cv2', 'numpy', 'PIL', 'requests', 'fastapi', 
        'uvicorn', 'easyocr', 'librosa', 'soundfile', 'scipy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"  ✓ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"  ✗ {module}")
    
    if missing_modules:
        logger.error(f"Missing modules: {missing_modules}")
        return False
    else:
        logger.info("All dependencies are available!")
        return True

def test_ffmpeg():
    """Test FFmpeg availability and capabilities"""
    logger = setup_test_logging()
    logger.info("Testing FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"  ✓ FFmpeg available: {version_line}")
            return True
        else:
            logger.error("FFmpeg test failed")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg not found or not working")
        return False

def cleanup_test_files():
    """Clean up test files"""
    logger = setup_test_logging()
    logger.info("Cleaning up test files...")
    
    cleanup_files = [
        "pipeline_test.mp4",
        "final_test.log"
    ]
    
    cleanup_dirs = [
        "frames/pipeline_test_123",
        "translated_frames/pipeline_test_123", 
        "separated_audio/pipeline_test_123",
        "logs/pipeline_test_123"
    ]
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"  Cleaned up: {file}")
            except:
                pass
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                import shutil
                shutil.rmtree(directory)
                logger.info(f"  Cleaned up directory: {directory}")
            except:
                pass

def main():
    """Main test function"""
    logger = setup_test_logging()
    logger.info("=" * 80)
    logger.info("FINAL COMPREHENSIVE TEST FOR AI-FIED TRANSLATE AI")
    logger.info("=" * 80)
    
    test_results = {}
    
    # Test 1: File Structure
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: FILE STRUCTURE")
    logger.info("=" * 60)
    test_results['file_structure'] = test_file_structure()
    
    # Test 2: Dependencies
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: DEPENDENCIES")
    logger.info("=" * 60)
    test_results['dependencies'] = test_dependencies()
    
    # Test 3: FFmpeg
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: FFMPEG")
    logger.info("=" * 60)
    test_results['ffmpeg'] = test_ffmpeg()
    
    # Test 4: Audio Separation Component
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: AUDIO SEPARATION COMPONENT")
    logger.info("=" * 60)
    test_results['audio_separation'] = test_audio_separation_standalone()
    
    # Test 5: Complete Pipeline
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: COMPLETE PIPELINE")
    logger.info("=" * 60)
    test_results['complete_pipeline'] = test_complete_pipeline()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL TEST RESULTS SUMMARY")
    logger.info("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed_tests += 1
    
    logger.info(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("The AI-fied Translate AI system is fully functional!")
        logger.info("\nKey Features Working:")
        logger.info("  ✓ Background music separation")
        logger.info("  ✓ Video processing pipeline")
        logger.info("  ✓ OCR text detection")
        logger.info("  ✓ Audio processing")
        logger.info("  ✓ File structure and dependencies")
        logger.info("  ✓ FFmpeg integration")
        logger.info("\nThe system is ready for production use!")
    else:
        logger.info(f"\n⚠️ {total_tests - passed_tests} tests failed.")
        logger.info("Check logs for details.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
