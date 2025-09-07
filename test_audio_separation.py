#!/usr/bin/env python3
"""
Test suite for audio separation functionality
Tests all separation methods and quality metrics
"""

import os
import sys
import tempfile
import numpy as np
import soundfile as sf
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_separator import AudioSeparator

def setup_test_logging():
    """Set up logging for tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_audio(duration=5, sample_rate=44100, filename="test_audio.wav"):
    """
    Create a test audio file with mixed voice and music content
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate
        filename: Output filename
        
    Returns:
        Path to created audio file
    """
    # Generate test signals
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Voice signal (speech-like frequencies)
    voice_freq = 200 + 100 * np.sin(2 * np.pi * 0.5 * t)  # Varying frequency
    voice_signal = 0.3 * np.sin(2 * np.pi * voice_freq * t)
    
    # Music signal (higher frequencies, more complex)
    music_signal = 0.2 * (
        np.sin(2 * np.pi * 440 * t) +  # A note
        0.5 * np.sin(2 * np.pi * 880 * t) +  # A octave
        0.3 * np.sin(2 * np.pi * 1320 * t)  # E note
    )
    
    # Add some noise and modulation
    voice_signal += 0.1 * np.random.randn(len(t))
    music_signal += 0.05 * np.random.randn(len(t))
    
    # Combine signals
    mixed_signal = voice_signal + music_signal
    
    # Normalize
    mixed_signal = mixed_signal / np.max(np.abs(mixed_signal)) * 0.8
    
    # Save to file
    sf.write(filename, mixed_signal, sample_rate)
    
    return filename

def test_custom_separation():
    """Test custom frequency-based separation"""
    logger = setup_test_logging()
    logger.info("🧪 Testing custom audio separation...")
    
    try:
        # Create test audio
        test_audio_path = create_test_audio(duration=3, filename="test_custom.wav")
        
        # Initialize separator
        separator = AudioSeparator(method="custom", logger=logger)
        
        # Perform separation
        result = separator.separate_audio(test_audio_path, "test_output")
        
        # Verify output files exist
        assert os.path.exists(result['voice']), "Voice file not created"
        assert os.path.exists(result['music']), "Music file not created"
        
        # Check file sizes
        voice_size = os.path.getsize(result['voice'])
        music_size = os.path.getsize(result['music'])
        assert voice_size > 1000, "Voice file too small"
        assert music_size > 1000, "Music file too small"
        
        # Test quality analysis
        quality = separator.get_separation_quality(
            test_audio_path, 
            result['voice'], 
            result['music']
        )
        
        assert 'overall_quality' in quality, "Quality metrics missing"
        assert quality['overall_quality'] >= 0, "Invalid quality score"
        
        logger.info("✅ Custom separation test passed")
        logger.info(f"Quality score: {quality['overall_quality']:.1f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Custom separation test failed: {e}")
        return False
    
    finally:
        # Cleanup
        cleanup_files = [
            "test_custom.wav",
            "test_output/test_custom_voice.wav",
            "test_output/test_custom_music.wav"
        ]
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists("test_output"):
            os.rmdir("test_output")

def test_spleeter_separation():
    """Test Spleeter-based separation (if available)"""
    logger = setup_test_logging()
    logger.info("🧪 Testing Spleeter audio separation...")
    
    try:
        # Create test audio
        test_audio_path = create_test_audio(duration=3, filename="test_spleeter.wav")
        
        # Initialize separator
        separator = AudioSeparator(method="spleeter", logger=logger)
        
        if not separator.spleeter_available:
            logger.info("⚠️ Spleeter not available, skipping test")
            return True
        
        # Perform separation
        result = separator.separate_audio(test_audio_path, "test_spleeter_output")
        
        # Verify output files exist
        assert os.path.exists(result['voice']), "Voice file not created"
        assert os.path.exists(result['music']), "Music file not created"
        
        logger.info("✅ Spleeter separation test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Spleeter separation test failed: {e}")
        return False
    
    finally:
        # Cleanup
        cleanup_files = [
            "test_spleeter.wav",
            "test_spleeter_output/test_spleeter_voice.wav",
            "test_spleeter_output/test_spleeter_music.wav"
        ]
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists("test_spleeter_output"):
            import shutil
            shutil.rmtree("test_spleeter_output")

def test_quality_metrics():
    """Test quality analysis functionality"""
    logger = setup_test_logging()
    logger.info("🧪 Testing quality metrics...")
    
    try:
        # Create test audio
        test_audio_path = create_test_audio(duration=2, filename="test_quality.wav")
        
        # Initialize separator
        separator = AudioSeparator(method="custom", logger=logger)
        
        # Perform separation
        result = separator.separate_audio(test_audio_path, "test_quality_output")
        
        # Test quality analysis
        quality = separator.get_separation_quality(
            test_audio_path,
            result['voice'],
            result['music']
        )
        
        # Verify quality metrics
        required_metrics = [
            'voice_snr', 'music_snr', 'voice_spectral_centroid',
            'music_spectral_centroid', 'overall_quality'
        ]
        
        for metric in required_metrics:
            assert metric in quality, f"Missing metric: {metric}"
            assert isinstance(quality[metric], (int, float)), f"Invalid metric type: {metric}"
        
        # Check quality score range
        assert 0 <= quality['overall_quality'] <= 100, "Quality score out of range"
        
        logger.info("✅ Quality metrics test passed")
        logger.info(f"Quality metrics: {quality}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quality metrics test failed: {e}")
        return False
    
    finally:
        # Cleanup
        cleanup_files = [
            "test_quality.wav",
            "test_quality_output/test_quality_voice.wav",
            "test_quality_output/test_quality_music.wav"
        ]
        for file in cleanup_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists("test_quality_output"):
            import shutil
            shutil.rmtree("test_quality_output")

def test_error_handling():
    """Test error handling for invalid inputs"""
    logger = setup_test_logging()
    logger.info("🧪 Testing error handling...")
    
    try:
        separator = AudioSeparator(method="custom", logger=logger)
        
        # Test with non-existent file
        try:
            separator.separate_audio("non_existent.wav")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            logger.info("✅ FileNotFoundError handled correctly")
        
        # Test with invalid method
        try:
            AudioSeparator(method="invalid_method")
            assert False, "Should have raised ValueError"
        except ValueError:
            logger.info("✅ Invalid method error handled correctly")
        
        logger.info("✅ Error handling test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run all audio separation tests"""
    logger = setup_test_logging()
    logger.info("🚀 Starting audio separation test suite...")
    
    tests = [
        ("Custom Separation", test_custom_separation),
        ("Spleeter Separation", test_spleeter_separation),
        ("Quality Metrics", test_quality_metrics),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST SUMMARY: {passed}/{total} tests passed")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
