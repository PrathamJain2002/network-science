#!/usr/bin/env python3
"""
Real API Test for AI-fied Translate AI
Uses real API keys from environment variables
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
            logging.FileHandler('real_api_test.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def check_api_keys():
    """Check if required API keys are available"""
    logger = setup_test_logging()
    logger.info("Checking API keys...")
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        logger.info("Please set your OpenAI API key:")
        logger.info("  Windows: set OPENAI_API_KEY=your-key-here")
        logger.info("  Linux/Mac: export OPENAI_API_KEY=your-key-here")
        return False
    else:
        logger.info(f"✓ OpenAI API key found: {openai_key[:10]}...")
    
    # Check Google credentials
    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not google_creds:
        # Check if the default file exists
        if os.path.exists('sampark-ai-bc13b9af3b55.json'):
            logger.info("✓ Google credentials file found: sampark-ai-bc13b9af3b55.json")
        else:
            logger.error("Google credentials not found")
            logger.info("Please set GOOGLE_APPLICATION_CREDENTIALS or ensure sampark-ai-bc13b9af3b55.json exists")
            return False
    else:
        logger.info(f"✓ Google credentials found: {google_creds}")
    
    return True

def create_test_video_with_hindi_text(duration=3, filename="hindi_test.mp4"):
    """Create a test video with Hindi text for real translation testing"""
    logger = setup_test_logging()
    logger.info(f"Creating test video with Hindi text: {filename}")
    
    try:
        # Create a video with Hindi text using FFmpeg
        # We'll create a simple video with Hindi text overlay
        cmd = [
            'ffmpeg',
            '-f', 'lavfi', '-i', f'testsrc=duration={duration}:size=640x480:rate=1',
            '-f', 'lavfi', '-i', f'sine=frequency=1000:duration={duration}',
            '-vf', 'drawtext=text="हिंदी में लिखा गया पाठ":fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', filename
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        logger.info(f"Test video with Hindi text created: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Failed to create test video: {e}")
        return None

def test_real_translation():
    """Test real translation using actual API keys"""
    logger = setup_test_logging()
    logger.info("Testing real translation with API keys...")
    
    try:
        # Create test video
        test_video = create_test_video_with_hindi_text(duration=2, filename="real_translation_test.mp4")
        if not test_video:
            logger.error("Failed to create test video")
            return False
        
        # Get API keys from environment
        openai_key = os.getenv('OPENAI_API_KEY')
        google_creds = 'sampark-ai-bc13b9af3b55.json'
        
        # Initialize video translator with real API keys
        translator = VideoTranslator(
            openai_api_key=openai_key,
            google_credentials_path=google_creds,
            font_path="noto-sans-devanagari/NotoSansDevanagari-Regular.ttf"
        )
        
        logger.info("Starting real video translation...")
        
        # Process video with real APIs
        result = translator.process_video(
            video_path=test_video,
            video_id="real_translation_test_123",
            advanced_ocr=True,
            moving_text=True,
            cleanup=False,  # Don't cleanup for inspection
            test_mode=True  # Use test mode for faster processing
        )
        
        if result:
            logger.info("Real video translation completed successfully!")
            
            # Check output files
            output_files = [
                "output/output_real_translation_test_123.mp4",
                "audios/audio_real_translation_test_123.wav",
                "separated_audio/real_translation_test_123/audio_real_translation_test_123_voice.wav",
                "separated_audio/real_translation_test_123/audio_real_translation_test_123_music.wav"
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
            logger.error("Real video translation failed")
            return False
            
    except Exception as e:
        logger.error(f"Real translation test failed: {e}")
        return False

def test_audio_separation_with_real_audio():
    """Test audio separation with real audio file"""
    logger = setup_test_logging()
    logger.info("Testing audio separation with real audio...")
    
    try:
        # Create a more complex audio file for testing
        test_audio = "real_audio_test.wav"
        cmd = [
            'ffmpeg',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3',
            '-f', 'lavfi', '-i', 'sine=frequency=2000:duration=3',
            '-filter_complex', '[0:a][1:a]amix=inputs=2:duration=first',
            '-y', test_audio
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Test audio separation
        separator = AudioSeparator(method="custom")
        result = separator.separate_audio(test_audio, "real_separation_test")
        
        if result and 'voice_track' in result and 'music_track' in result:
            logger.info("Real audio separation working correctly!")
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
            if os.path.exists("real_separation_test"):
                shutil.rmtree("real_separation_test")
            
            return True
        else:
            logger.error("Real audio separation failed")
            return False
            
    except Exception as e:
        logger.error(f"Real audio separation test failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    logger = setup_test_logging()
    logger.info("Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        
        openai_key = os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=openai_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Translate 'Hello' to Hindi"}
            ],
            max_tokens=10
        )
        
        translation = response.choices[0].message.content
        logger.info(f"OpenAI API test successful! Translation: {translation}")
        return True
        
    except Exception as e:
        logger.error(f"OpenAI API test failed: {e}")
        return False

def test_google_tts_connection():
    """Test Google TTS connection"""
    logger = setup_test_logging()
    logger.info("Testing Google TTS connection...")
    
    try:
        from google.cloud import texttospeech
        
        # Initialize the client
        client = texttospeech.TextToSpeechClient()
        
        # Test with a simple synthesis request
        synthesis_input = texttospeech.SynthesisInput(text="Hello")
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        logger.info("Google TTS API test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Google TTS API test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files"""
    logger = setup_test_logging()
    logger.info("Cleaning up test files...")
    
    cleanup_files = [
        "hindi_test.mp4",
        "real_translation_test.mp4",
        "real_api_test.log"
    ]
    
    cleanup_dirs = [
        "frames/real_translation_test_123",
        "translated_frames/real_translation_test_123", 
        "separated_audio/real_translation_test_123",
        "logs/real_translation_test_123"
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
    logger.info("REAL API TEST FOR AI-FIED TRANSLATE AI")
    logger.info("=" * 80)
    
    # Check API keys first
    if not check_api_keys():
        logger.error("API keys not configured. Please set up your API keys first.")
        return False
    
    test_results = {}
    
    # Test 1: OpenAI API Connection
    logger.info("\n" + "=" * 60)
    logger.info("TEST 1: OPENAI API CONNECTION")
    logger.info("=" * 60)
    test_results['openai_connection'] = test_openai_connection()
    
    # Test 2: Google TTS Connection
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: GOOGLE TTS CONNECTION")
    logger.info("=" * 60)
    test_results['google_tts_connection'] = test_google_tts_connection()
    
    # Test 3: Real Audio Separation
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: REAL AUDIO SEPARATION")
    logger.info("=" * 60)
    test_results['real_audio_separation'] = test_audio_separation_with_real_audio()
    
    # Test 4: Real Translation Pipeline
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: REAL TRANSLATION PIPELINE")
    logger.info("=" * 60)
    test_results['real_translation'] = test_real_translation()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("REAL API TEST RESULTS SUMMARY")
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
        logger.info("\n🎉 ALL REAL API TESTS PASSED!")
        logger.info("The AI-fied Translate AI system is working with real APIs!")
        logger.info("\nVerified Features:")
        logger.info("  ✓ OpenAI API connection and translation")
        logger.info("  ✓ Google TTS API connection")
        logger.info("  ✓ Real audio separation")
        logger.info("  ✓ Complete translation pipeline with real APIs")
        logger.info("\nThe system is ready for production use with real API keys!")
    else:
        logger.info(f"\n⚠️ {total_tests - passed_tests} tests failed.")
        logger.info("Check logs for details.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
