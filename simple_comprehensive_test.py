#!/usr/bin/env python3
"""
Simple Comprehensive Test for AI-fied Translate AI
Tests core functionality without server dependencies
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
            logging.FileHandler('simple_test.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def create_test_video(duration=3, filename="simple_test.mp4", fps=15):
    """Create a test video optimized for testing"""
    logger = setup_test_logging()
    logger.info(f"Creating test video: {filename} (duration: {duration}s)")
    
    try:
        # Create video with lower resolution for faster processing
        width, height = 640, 480
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        # Create frames with Hindi text
        for frame_num in range(duration * fps):
            # Create frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame.fill(255)  # White background
            
            # Add Hindi text
            cv2.putText(frame, f"Hindi Text {frame_num}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(frame, f"Frame: {frame_num}", (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Add visual elements
            cv2.rectangle(frame, (100, 200), (500, 300), (0, 255, 0), 2)
            cv2.circle(frame, (300, 400), 50, (255, 0, 0), -1)
            
            out.write(frame)
        
        out.release()
        
        # Convert to proper MP4 format with audio
        final_filename = filename.replace('.mp4', '_final.mp4')
        cmd = ['ffmpeg', '-i', filename, '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=2', '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', final_filename]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Clean up temporary file
        if os.path.exists(filename):
            os.remove(filename)
        
        logger.info(f"Test video created: {final_filename}")
        return final_filename
        
    except Exception as e:
        logger.error(f"Failed to create test video: {e}")
        return None

def test_audio_separation():
    """Test audio separation functionality"""
    logger = setup_test_logging()
    logger.info("Testing audio separation...")
    
    try:
        # Create test audio file
        test_audio = "test_audio.wav"
        cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3', '-y', test_audio]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Test audio separation
        separator = AudioSeparator(method="custom")
        result = separator.separate_audio(test_audio, "test_separation_output")
        
        logger.info(f"Audio separation result: {result}")
        
        if result and 'voice_track' in result and 'music_track' in result:
            logger.info("Audio separation test PASSED")
            
            # Test quality metrics
            try:
                quality = separator.get_separation_quality(test_audio, result['voice_track'], result['music_track'])
                logger.info(f"Separation quality: {quality}")
            except Exception as e:
                logger.warning(f"Quality metrics failed: {e}")
            
            # Cleanup
            os.remove(test_audio)
            import shutil
            if os.path.exists("test_separation_output"):
                shutil.rmtree("test_separation_output")
            
            return True
        else:
            logger.error("Audio separation test FAILED")
            # Cleanup even on failure
            if os.path.exists(test_audio):
                os.remove(test_audio)
            import shutil
            if os.path.exists("test_separation_output"):
                shutil.rmtree("test_separation_output")
            return False
            
    except Exception as e:
        logger.error(f"Audio separation test failed: {e}")
        return False

def test_video_processing():
    """Test video processing with test mode"""
    logger = setup_test_logging()
    logger.info("Testing video processing...")
    
    try:
        # Create test video
        test_video = create_test_video(duration=2, filename="processing_test.mp4")
        if not test_video:
            logger.error("Failed to create test video")
            return False
        
        # Initialize video translator
        translator = VideoTranslator(
            openai_api_key="test-key",  # Will use mock data
            google_credentials_path="sampark-ai-bc13b9af3b55.json",
            font_path="noto-sans-devanagari/NotoSansDevanagari-Regular.ttf"
        )
        
        # Process video in test mode
        result = translator.process_video(
            video_path=test_video,
            video_id="processing_test_123",
            advanced_ocr=True,
            moving_text=True,
            cleanup=False,  # Don't cleanup for inspection
            test_mode=True  # Use test mode for faster processing
        )
        
        if result:
            logger.info("Video processing test PASSED")
            
            # Check if output files exist
            output_files = [
                "output/output_processing_test_123.mp4",
                "audios/audio_processing_test_123.wav",
                "separated_audio/processing_test_123/audio_processing_test_123_voice.wav",
                "separated_audio/processing_test_123/audio_processing_test_123_music.wav"
            ]
            
            for file_path in output_files:
                if os.path.exists(file_path):
                    logger.info(f"Output file exists: {file_path}")
                else:
                    logger.warning(f"Output file missing: {file_path}")
            
            return True
        else:
            logger.error("Video processing test FAILED")
            return False
            
    except Exception as e:
        logger.error(f"Video processing test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and dependencies"""
    logger = setup_test_logging()
    logger.info("Testing file structure...")
    
    required_files = [
        "api.py",
        "video_translator.py", 
        "audio_separator.py",
        "server.js",
        "requirements.txt",
        "package.json"
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
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_files or missing_dirs:
        logger.error(f"Missing files: {missing_files}")
        logger.error(f"Missing directories: {missing_dirs}")
        return False
    else:
        logger.info("File structure test PASSED")
        return True

def test_dependencies():
    """Test Python dependencies"""
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
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"Missing modules: {missing_modules}")
        return False
    else:
        logger.info("Dependencies test PASSED")
        return True

def test_ffmpeg():
    """Test FFmpeg availability"""
    logger = setup_test_logging()
    logger.info("Testing FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("FFmpeg test PASSED")
            return True
        else:
            logger.error("FFmpeg test FAILED")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg not found or not working")
        return False

def cleanup_test_files():
    """Clean up test files"""
    logger = setup_test_logging()
    logger.info("Cleaning up test files...")
    
    cleanup_files = [
        "simple_test_final.mp4",
        "processing_test_final.mp4",
        "simple_test.log"
    ]
    
    cleanup_dirs = [
        "frames/processing_test_123",
        "translated_frames/processing_test_123", 
        "separated_audio/processing_test_123",
        "logs/processing_test_123"
    ]
    
    for file in cleanup_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"Cleaned up: {file}")
            except:
                pass
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            try:
                import shutil
                shutil.rmtree(directory)
                logger.info(f"Cleaned up directory: {directory}")
            except:
                pass

def main():
    """Main test function"""
    logger = setup_test_logging()
    logger.info("Starting Simple Comprehensive Test Suite...")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test 1: File Structure
    logger.info("\n" + "=" * 60)
    logger.info("Testing File Structure")
    logger.info("=" * 60)
    test_results['file_structure'] = test_file_structure()
    
    # Test 2: Dependencies
    logger.info("\n" + "=" * 60)
    logger.info("Testing Dependencies")
    logger.info("=" * 60)
    test_results['dependencies'] = test_dependencies()
    
    # Test 3: FFmpeg
    logger.info("\n" + "=" * 60)
    logger.info("Testing FFmpeg")
    logger.info("=" * 60)
    test_results['ffmpeg'] = test_ffmpeg()
    
    # Test 4: Audio Separation
    logger.info("\n" + "=" * 60)
    logger.info("Testing Audio Separation")
    logger.info("=" * 60)
    test_results['audio_separation'] = test_audio_separation()
    
    # Test 5: Video Processing
    logger.info("\n" + "=" * 60)
    logger.info("Testing Video Processing")
    logger.info("=" * 60)
    test_results['video_processing'] = test_video_processing()
    
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
        logger.info("ALL TESTS PASSED! The AI-fied Translate AI system is working correctly!")
    else:
        logger.info(f"{total_tests - passed_tests} tests failed. Check logs for details.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
