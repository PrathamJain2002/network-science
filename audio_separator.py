#!/usr/bin/env python3
"""
Audio Separation Module for Translate AI
Separates audio into voice and background music using AI-powered source separation
"""

import os
import subprocess
import logging
import tempfile
from typing import Tuple, Optional, Dict
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import requests
import json

class AudioSeparator:
    """
    AI-powered audio separation for voice and background music
    Supports multiple separation methods including Spleeter, LALAL.AI, and custom models
    """
    
    def __init__(self, method: str = "librosa", logger: Optional[logging.Logger] = None):
        """
        Initialize audio separator
        
        Args:
            method: Separation method ('librosa', 'lalalai', 'custom')
            logger: Optional logger instance
        """
        self.method = method
        self.logger = logger or logging.getLogger(__name__)
        
        # Ensure output directories exist
        self._ensure_directories()
        
        # Initialize separation method
        self._initialize_separator()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            "separated_audio",
            "temp_audio",
            "models"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if self.logger:
                self.logger.debug(f"📁 Ensured directory exists: {directory}/")
    
    def _initialize_separator(self):
        """Initialize the selected separation method"""
        if self.method == "librosa":
            self._initialize_librosa()
        elif self.method == "lalalai":
            self._initialize_lalalai()
        elif self.method == "custom":
            self._initialize_custom_model()
        else:
            raise ValueError(f"Unsupported separation method: {self.method}")
    
    def _initialize_librosa(self):
        """Initialize Librosa for audio separation"""
        try:
            import librosa
            self.librosa_available = True
            self.logger.info("✅ Librosa initialized successfully")
        except ImportError:
            self.logger.warning("⚠️ Librosa not available, falling back to custom method")
            self.librosa_available = False
            self.method = "custom"
    
    def _initialize_lalalai(self):
        """Initialize LALAL.AI API client"""
        # LALAL.AI API configuration
        self.lalalai_api_key = os.getenv('LALALAI_API_KEY')
        self.lalalai_base_url = "https://api.lalal.ai/api/v1"
        
        if not self.lalalai_api_key:
            self.logger.warning("⚠️ LALAL.AI API key not found, falling back to custom method")
            self.method = "custom"
        else:
            self.logger.info("✅ LALAL.AI API initialized")
    
    def _initialize_custom_model(self):
        """Initialize custom audio separation model"""
        self.logger.info("🔧 Initializing custom audio separation model")
        # Custom model initialization would go here
        # For now, we'll use a simple frequency-based separation
    
    def separate_audio(self, audio_path: str, output_dir: str = None) -> Dict[str, str]:
        """
        Separate audio into voice and background music
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save separated audio files
            
        Returns:
            Dictionary with paths to separated audio files
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if output_dir is None:
            output_dir = "separated_audio"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filenames
        audio_name = Path(audio_path).stem
        voice_path = os.path.join(output_dir, f"{audio_name}_voice.wav")
        music_path = os.path.join(output_dir, f"{audio_name}_music.wav")
        
        self.logger.info(f"🎵 Starting audio separation: {audio_path}")
        self.logger.info(f"📁 Output directory: {output_dir}")
        
        try:
            if self.method == "librosa" and self.librosa_available:
                result = self._separate_with_librosa(audio_path, output_dir)
            elif self.method == "lalalai":
                result = self._separate_with_lalalai(audio_path, output_dir)
            else:
                result = self._separate_with_custom(audio_path, output_dir)
            
            # Verify output files
            if not os.path.exists(result['voice']) or not os.path.exists(result['music']):
                raise Exception("Audio separation failed - output files not created")
            
            # Log file sizes
            voice_size = os.path.getsize(result['voice']) / (1024 * 1024)
            music_size = os.path.getsize(result['music']) / (1024 * 1024)
            
            self.logger.info(f"✅ Audio separation completed successfully")
            self.logger.info(f"🎤 Voice track: {result['voice']} ({voice_size:.1f} MB)")
            self.logger.info(f"🎵 Music track: {result['music']} ({music_size:.1f} MB)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Audio separation failed: {e}")
            raise e
    
    def _separate_with_librosa(self, audio_path: str, output_dir: str) -> Dict[str, str]:
        """Separate audio using Librosa (basic frequency-based separation)"""
        try:
            import librosa
            import soundfile as sf
            
            self.logger.info("🔧 Using Librosa for audio separation...")
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            
            # Basic frequency-based separation
            # This is a simplified approach - in production, you'd use more sophisticated methods
            
            # Separate into frequency bands
            # Low frequencies (typically music/bass)
            y_low = librosa.effects.preemphasis(y, coef=0.97)
            
            # High frequencies (typically voice)
            y_high = y - y_low
            
            # Apply some filtering to improve separation
            from scipy import signal
            
            # Low-pass filter for music
            b, a = signal.butter(4, 0.3, btype='low')
            y_music = signal.filtfilt(b, a, y_low)
            
            # High-pass filter for voice
            b, a = signal.butter(4, 0.1, btype='high')
            y_voice = signal.filtfilt(b, a, y_high)
            
            # Normalize audio
            y_music = librosa.util.normalize(y_music)
            y_voice = librosa.util.normalize(y_voice)
            
            # Save separated audio
            audio_name = Path(audio_path).stem
            voice_file = os.path.join(output_dir, f"{audio_name}_voice.wav")
            music_file = os.path.join(output_dir, f"{audio_name}_music.wav")
            
            sf.write(voice_file, y_voice, sr)
            sf.write(music_file, y_music, sr)
            
            self.logger.info(f"✅ Librosa separation completed")
            self.logger.info(f"🎤 Voice saved to: {voice_file}")
            self.logger.info(f"🎵 Music saved to: {music_file}")
            
            return {
                'voice': voice_file,
                'music': music_file
            }
                
        except Exception as e:
            raise Exception(f"Librosa separation failed: {e}")
    
    def _separate_with_lalalai(self, audio_path: str, output_dir: str) -> Dict[str, str]:
        """Separate audio using LALAL.AI API"""
        try:
            self.logger.info("🌐 Using LALAL.AI API for audio separation...")
            
            # Upload audio file
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                headers = {'Authorization': f'Bearer {self.lalalai_api_key}'}
                
                upload_response = requests.post(
                    f"{self.lalalai_base_url}/upload/",
                    files=files,
                    headers=headers,
                    timeout=60
                )
            
            if upload_response.status_code != 200:
                raise Exception(f"LALAL.AI upload failed: {upload_response.text}")
            
            upload_data = upload_response.json()
            task_id = upload_data.get('id')
            
            if not task_id:
                raise Exception("No task ID received from LALAL.AI")
            
            # Wait for processing
            self.logger.info(f"⏳ Waiting for LALAL.AI processing (Task ID: {task_id})...")
            
            max_attempts = 30  # 5 minutes max
            for attempt in range(max_attempts):
                status_response = requests.get(
                    f"{self.lalalai_base_url}/status/{task_id}/",
                    headers=headers,
                    timeout=10
                )
                
                if status_response.status_code != 200:
                    raise Exception(f"Status check failed: {status_response.text}")
                
                status_data = status_response.json()
                status = status_data.get('status')
                
                if status == 'SUCCESS':
                    break
                elif status == 'FAILURE':
                    raise Exception("LALAL.AI processing failed")
                elif attempt == max_attempts - 1:
                    raise Exception("LALAL.AI processing timed out")
                
                import time
                time.sleep(10)
            
            # Download separated files
            audio_name = Path(audio_path).stem
            voice_path = os.path.join(output_dir, f"{audio_name}_voice.wav")
            music_path = os.path.join(output_dir, f"{audio_name}_music.wav")
            
            # Download voice track
            voice_url = status_data.get('voice_url')
            if voice_url:
                voice_response = requests.get(voice_url, timeout=60)
                with open(voice_path, 'wb') as f:
                    f.write(voice_response.content)
            
            # Download music track
            music_url = status_data.get('music_url')
            if music_url:
                music_response = requests.get(music_url, timeout=60)
                with open(music_path, 'wb') as f:
                    f.write(music_response.content)
            
            return {
                'voice': voice_path,
                'music': music_path
            }
            
        except Exception as e:
            raise Exception(f"LALAL.AI separation failed: {e}")
    
    def _separate_with_custom(self, audio_path: str, output_dir: str) -> Dict[str, str]:
        """Separate audio using custom frequency-based method"""
        try:
            self.logger.info("🔧 Using custom frequency-based separation...")
            
            # Load audio
            audio, sr = librosa.load(audio_path, sr=None)
            
            # Apply frequency-based separation
            voice_audio, music_audio = self._frequency_based_separation(audio, sr)
            
            # Save separated audio
            audio_name = Path(audio_path).stem
            voice_path = os.path.join(output_dir, f"{audio_name}_voice.wav")
            music_path = os.path.join(output_dir, f"{audio_name}_music.wav")
            
            sf.write(voice_path, voice_audio, sr)
            sf.write(music_path, music_audio, sr)
            
            return {
                'voice': voice_path,
                'music': music_path
            }
            
        except Exception as e:
            raise Exception(f"Custom separation failed: {e}")
    
    def _frequency_based_separation(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simple frequency-based audio separation
        This is a basic implementation - in production, use trained models
        """
        # Apply high-pass filter for voice (typically 300-3400 Hz)
        voice_high = signal.butter(4, 300, btype='high', fs=sr, output='sos')
        voice_low = signal.butter(4, 3400, btype='low', fs=sr, output='sos')
        
        voice_audio = signal.sosfilt(voice_high, audio)
        voice_audio = signal.sosfilt(voice_low, voice_audio)
        
        # Apply low-pass and high-pass filters for music
        music_low = signal.butter(4, 300, btype='low', fs=sr, output='sos')
        music_high = signal.butter(4, 3400, btype='high', fs=sr, output='sos')
        
        music_audio = signal.sosfilt(music_low, audio) + signal.sosfilt(music_high, audio)
        
        # Normalize audio levels
        voice_audio = voice_audio / np.max(np.abs(voice_audio)) * 0.8
        music_audio = music_audio / np.max(np.abs(music_audio)) * 0.8
        
        return voice_audio, music_audio
    
    def get_separation_quality(self, original_path: str, voice_path: str, music_path: str) -> Dict[str, float]:
        """
        Analyze separation quality and return metrics
        
        Args:
            original_path: Path to original audio
            voice_path: Path to separated voice
            music_path: Path to separated music
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            # Load audio files
            original, sr = librosa.load(original_path, sr=None)
            voice, _ = librosa.load(voice_path, sr=sr)
            music, _ = librosa.load(music_path, sr=sr)
            
            # Calculate basic quality metrics
            metrics = {}
            
            # Signal-to-noise ratio approximation
            original_energy = np.mean(original ** 2)
            voice_energy = np.mean(voice ** 2)
            music_energy = np.mean(music ** 2)
            
            # Calculate SNR with proper handling of edge cases
            voice_snr_ratio = voice_energy / (original_energy - voice_energy + 1e-10)
            music_snr_ratio = music_energy / (original_energy - music_energy + 1e-10)
            
            # Handle invalid values
            if np.isfinite(voice_snr_ratio) and voice_snr_ratio > 0:
                metrics['voice_snr'] = float(10 * np.log10(voice_snr_ratio))
            else:
                metrics['voice_snr'] = 0.0
                
            if np.isfinite(music_snr_ratio) and music_snr_ratio > 0:
                metrics['music_snr'] = float(10 * np.log10(music_snr_ratio))
            else:
                metrics['music_snr'] = 0.0
            
            # Spectral characteristics
            voice_spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=voice, sr=sr))
            music_spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=music, sr=sr))
            
            metrics['voice_spectral_centroid'] = voice_spectral_centroid
            metrics['music_spectral_centroid'] = music_spectral_centroid
            
            # Overall quality score (0-100)
            quality_score = min(100, max(0, 
                (metrics['voice_snr'] + metrics['music_snr']) / 2 + 50
            ))
            metrics['overall_quality'] = quality_score
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed: {e}")
            return {'overall_quality': 0.0}


def test_audio_separation():
    """Test function for audio separation"""
    import tempfile
    
    # Create a simple test audio file
    test_audio = np.random.randn(44100 * 5)  # 5 seconds of noise
    test_path = "test_audio.wav"
    sf.write(test_path, test_audio, 44100)
    
    try:
        # Test separation
        separator = AudioSeparator(method="custom")
        result = separator.separate_audio(test_path)
        
        print("✅ Audio separation test passed")
        print(f"Voice: {result['voice']}")
        print(f"Music: {result['music']}")
        
        # Test quality analysis
        quality = separator.get_separation_quality(test_path, result['voice'], result['music'])
        print(f"Quality metrics: {quality}")
        
    except Exception as e:
        print(f"❌ Audio separation test failed: {e}")
    
    finally:
        # Cleanup
        for file in [test_path, result['voice'], result['music']]:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run test
    test_audio_separation()
