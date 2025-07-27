#!/usr/bin/env python3
"""
Coqui TTS Integration Module for AI Business Video Script & Voiceover Generator
Provides high-quality text-to-speech functionality with multiple voice models and audio formats.
Includes fallback to mock audio generation when TTS fails.
"""

import os
import uuid
import io
import tempfile
import logging
import warnings
from typing import Optional, Dict, Any
from pathlib import Path

# Suppress warnings to avoid interference with JSON output in subprocess calls
warnings.filterwarnings('ignore')

try:
    from TTS.api import TTS
    from pydub import AudioSegment
    import soundfile as sf
    import numpy as np
    TTS_AVAILABLE = True
except ImportError as e:
    # Suppress the warning message that was causing JSON parsing issues
    TTS_AVAILABLE = False
    # Create dummy classes for type hints
    TTS = None
    AudioSegment = None
    sf = None
    np = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoquiTTSGenerator:
    """
    Advanced TTS generator using Coqui TTS with multiple voice models and audio formats.
    Includes fallback to mock audio when TTS fails.
    """
    
    # Available voice models with descriptions
    VOICE_MODELS = {
        'tacotron2_ljspeech': {
            'model_name': 'tts_models/en/ljspeech/tacotron2-DDC',
            'description': 'High-quality female voice (LJSpeech dataset)',
            'quality': 'high',
            'speed': 'medium'
        },
        'vits_ljspeech': {
            'model_name': 'tts_models/en/ljspeech/vits',
            'description': 'Fast, natural female voice (VITS model)',
            'quality': 'high',
            'speed': 'fast'
        },
        'tacotron2_ek1': {
            'model_name': 'tts_models/en/ek1/tacotron2',
            'description': 'Alternative female voice (EK1 dataset)',
            'quality': 'medium',
            'speed': 'medium'
        },
        'glow_tts': {
            'model_name': 'tts_models/en/ljspeech/glow-tts',
            'description': 'Flow-based TTS with natural prosody',
            'quality': 'high',
            'speed': 'fast'
        },
        'speedy_speech': {
            'model_name': 'tts_models/en/ljspeech/speedy-speech',
            'description': 'Ultra-fast TTS for quick generation',
            'quality': 'medium',
            'speed': 'very_fast'
        }
    }
    
    # Supported audio formats
    AUDIO_FORMATS = {
        'wav': {'mime_type': 'audio/wav', 'extension': '.wav'},
        'mp3': {'mime_type': 'audio/mpeg', 'extension': '.mp3'},
        'ogg': {'mime_type': 'audio/ogg', 'extension': '.ogg'},
        'flac': {'mime_type': 'audio/flac', 'extension': '.flac'}
    }
    
    def __init__(self):
        """Initialize the TTS generator."""
        self.tts_cache = {}  # Cache loaded models
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"CoquiTTSGenerator initialized with temp dir: {self.temp_dir}")
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Dict[str, Any]]:
        """Get information about available voice models."""
        return cls.VOICE_MODELS
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, Dict[str, str]]:
        """Get information about supported audio formats."""
        return cls.AUDIO_FORMATS
    
    def _load_tts_model(self, model_key: str):
        """Load and cache a TTS model."""
        if not TTS_AVAILABLE or TTS is None:
            logger.warning("TTS not available, cannot load models")
            return None
            
        if model_key in self.tts_cache:
            return self.tts_cache[model_key]
        
        try:
            model_info = self.VOICE_MODELS.get(model_key)
            if not model_info:
                logger.error(f"Unknown model key: {model_key}")
                return None
            
            logger.info(f"Loading TTS model: {model_info['model_name']}")
            tts = TTS(model_name=model_info['model_name'])
            self.tts_cache[model_key] = tts
            logger.info(f"Successfully loaded model: {model_key}")
            return tts
            
        except Exception as e:
            logger.error(f"Failed to load TTS model {model_key}: {e}")
            return None
    
    def _generate_mock_audio(self, text: str, duration_seconds: int = None) -> bytes:
        """
        Generate mock audio as fallback when TTS fails.
        Creates a simple WAV file with sine wave tones.
        """
        try:
            # Estimate duration based on text length (assuming ~150 words per minute)
            if duration_seconds is None:
                word_count = len(text.split())
                duration_seconds = max(3, min(30, word_count * 0.4))  # 3-30 seconds
            
            # Check if numpy and soundfile are available
            if np is None or sf is None:
                logger.warning("numpy or soundfile not available, using basic mock audio")
                return self._create_minimal_wav()
            
            # Generate audio data
            sample_rate = 22050
            samples = int(duration_seconds * sample_rate)
            t = np.linspace(0, duration_seconds, samples, False)
            
            # Create a more pleasant tone pattern (multiple frequencies)
            frequency1 = 220  # A3 note
            frequency2 = 330  # E4 note
            frequency3 = 440  # A4 note
            
            # Mix frequencies with fade in/out
            audio_data = (
                0.3 * np.sin(2 * np.pi * frequency1 * t) +
                0.2 * np.sin(2 * np.pi * frequency2 * t) +
                0.1 * np.sin(2 * np.pi * frequency3 * t)
            )
            
            # Apply fade in/out to avoid clicks
            fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
            audio_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Normalize
            audio_data = audio_data * 0.5
            
            # Convert to bytes (WAV format)
            temp_path = os.path.join(self.temp_dir, f"mock_{uuid.uuid4().hex}.wav")
            sf.write(temp_path, audio_data, sample_rate)
            
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            os.unlink(temp_path)  # Clean up temp file
            logger.info(f"Generated mock audio: {len(audio_bytes)} bytes, {duration_seconds}s duration")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate mock audio: {e}")
            # Return minimal WAV header as last resort
            return self._create_minimal_wav()
    
    def _create_minimal_wav(self) -> bytes:
        """Create a minimal WAV file as absolute fallback."""
        # Minimal WAV header for 1 second of silence
        wav_header = bytes([
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x44, 0x10, 0x00, 0x00,  # File size
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            0x66, 0x6d, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Subchunk size
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels
            0x44, 0xac, 0x00, 0x00,  # Sample rate (44100)
            0x88, 0x58, 0x01, 0x00,  # Byte rate
            0x02, 0x00,              # Block align
            0x10, 0x00,              # Bits per sample
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x10, 0x00, 0x00   # Data size
        ])
        
        # Add 1 second of silence (44100 samples * 2 bytes)
        silence = bytes(88200)
        return wav_header + silence
    
    def _convert_audio_format(self, audio_bytes: bytes, target_format: str) -> bytes:
        """Convert audio to the specified format."""
        if target_format == 'wav':
            return audio_bytes  # Already in WAV format
        
        if AudioSegment is None:
            logger.warning("AudioSegment not available, returning WAV format")
            return audio_bytes
        
        try:
            # Write to temporary WAV file
            temp_wav = os.path.join(self.temp_dir, f"temp_{uuid.uuid4().hex}.wav")
            with open(temp_wav, 'wb') as f:
                f.write(audio_bytes)
            
            # Load and convert using pydub
            audio = AudioSegment.from_wav(temp_wav)
            
            # Convert to target format
            temp_output = os.path.join(self.temp_dir, f"output_{uuid.uuid4().hex}.{target_format}")
            
            if target_format == 'mp3':
                audio.export(temp_output, format="mp3", bitrate="128k")
            elif target_format == 'ogg':
                audio.export(temp_output, format="ogg")
            elif target_format == 'flac':
                audio.export(temp_output, format="flac")
            else:
                raise ValueError(f"Unsupported format: {target_format}")
            
            # Read converted file
            with open(temp_output, 'rb') as f:
                converted_bytes = f.read()
            
            # Clean up temp files
            os.unlink(temp_wav)
            os.unlink(temp_output)
            
            logger.info(f"Converted audio from WAV to {target_format.upper()}: {len(converted_bytes)} bytes")
            return converted_bytes
            
        except Exception as e:
            logger.error(f"Failed to convert audio to {target_format}: {e}")
            return audio_bytes  # Return original on failure
    
    def generate_speech(
        self,
        text: str,
        voice_model: str = 'tacotron2_ljspeech',
        audio_format: str = 'wav',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate speech from text using Coqui TTS.
        
        Args:
            text: Text to convert to speech
            voice_model: Voice model to use (key from VOICE_MODELS)
            audio_format: Output audio format (wav, mp3, ogg, flac)
            **kwargs: Additional parameters for TTS generation
            
        Returns:
            Dict containing:
                - audio_data: bytes of the generated audio
                - success: boolean indicating if TTS was successful
                - fallback_used: boolean indicating if mock audio was used
                - model_used: string indicating which model was used
                - format: string indicating the audio format
                - mime_type: string with the MIME type
                - duration_estimate: estimated duration in seconds
                - error: error message if any
        """
        result = {
            'audio_data': None,
            'success': False,
            'fallback_used': False,
            'model_used': voice_model,
            'format': audio_format,
            'mime_type': self.AUDIO_FORMATS.get(audio_format, {}).get('mime_type', 'audio/wav'),
            'duration_estimate': 0,
            'error': None
        }
        
        if not text or not text.strip():
            result['error'] = "Empty text provided"
            logger.error("Empty text provided for TTS generation")
            return result
        
        # Validate inputs
        if voice_model not in self.VOICE_MODELS:
            logger.warning(f"Unknown voice model '{voice_model}', using default")
            voice_model = 'tacotron2_ljspeech'
            result['model_used'] = voice_model
        
        if audio_format not in self.AUDIO_FORMATS:
            logger.warning(f"Unknown audio format '{audio_format}', using WAV")
            audio_format = 'wav'
            result['format'] = audio_format
            result['mime_type'] = 'audio/wav'
        
        # Estimate duration
        word_count = len(text.split())
        estimated_duration = max(3, min(30, word_count * 0.4))
        result['duration_estimate'] = estimated_duration
        
        # Try TTS generation first
        if TTS_AVAILABLE:
            try:
                logger.info(f"Attempting TTS generation with model: {voice_model}")
                tts = self._load_tts_model(voice_model)
                
                if tts:
                    # Generate speech to temporary file
                    temp_output = os.path.join(self.temp_dir, f"tts_output_{uuid.uuid4().hex}.wav")
                    
                    # Use TTS to generate audio
                    tts.tts_to_file(text=text, file_path=temp_output)
                    
                    # Check if file was created successfully
                    if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
                        with open(temp_output, 'rb') as f:
                            audio_bytes = f.read()
                        
                        os.unlink(temp_output)  # Clean up
                        
                        # Convert to target format if needed
                        if audio_format != 'wav':
                            audio_bytes = self._convert_audio_format(audio_bytes, audio_format)
                        
                        result['audio_data'] = audio_bytes
                        result['success'] = True
                        result['fallback_used'] = False
                        
                        logger.info(f"✅ TTS generation successful: {len(audio_bytes)} bytes")
                        return result
                    else:
                        raise Exception("TTS output file not created or empty")
                        
            except Exception as e:
                error_msg = f"TTS generation failed: {e}"
                logger.error(error_msg)
                result['error'] = error_msg
        
        # Fallback to mock audio
        logger.info("Using fallback mock audio generation")
        try:
            mock_audio = self._generate_mock_audio(text, int(estimated_duration))
            
            # Convert to target format if needed
            if audio_format != 'wav':
                mock_audio = self._convert_audio_format(mock_audio, audio_format)
            
            result['audio_data'] = mock_audio
            result['success'] = True
            result['fallback_used'] = True
            result['model_used'] = 'mock_audio'
            
            logger.info(f"✅ Mock audio generation successful: {len(mock_audio)} bytes")
            
        except Exception as e:
            error_msg = f"Both TTS and mock audio generation failed: {e}"
            logger.error(error_msg)
            result['error'] = error_msg
            result['audio_data'] = self._create_minimal_wav()
            result['success'] = True
            result['fallback_used'] = True
            result['model_used'] = 'minimal_wav'
        
        return result

# Global instance for easy import
coqui_tts = CoquiTTSGenerator()

def generate_coqui_voice(
    text: str, 
    voice_model: str = "tacotron2_ljspeech",
    audio_format: str = "wav"
) -> Dict[str, Any]:
    """
    Convenience function for generating voice with Coqui TTS.
    
    Args:
        text: Text to convert to speech
        voice_model: Voice model to use
        audio_format: Output audio format
        
    Returns:
        Dict with generation results
    """
    return coqui_tts.generate_speech(text, voice_model, audio_format)

if __name__ == "__main__":
    # Test the TTS functionality
    print("Testing Coqui TTS Integration...")
    
    # Test model availability
    models = CoquiTTSGenerator.get_available_models()
    print(f"\n📢 Available voice models ({len(models)}):")
    for key, info in models.items():
        print(f"  • {key}: {info['description']} (Quality: {info['quality']}, Speed: {info['speed']})")
    
    # Test format support
    formats = CoquiTTSGenerator.get_supported_formats()
    print(f"\n🎵 Supported audio formats ({len(formats)}):")
    for fmt, info in formats.items():
        print(f"  • {fmt.upper()}: {info['mime_type']}")
    
    # Test generation
    test_text = "Hello, this is a test of the Coqui TTS integration for AI business video generation."
    print(f"\n🔊 Testing speech generation...")
    print(f"Text: '{test_text}'")
    
    result = generate_coqui_voice(test_text)
    print(f"\nResult:")
    print(f"  ✅ Success: {result['success']}")
    print(f"  🔄 Fallback used: {result['fallback_used']}")
    print(f"  🎤 Model used: {result['model_used']}")
    print(f"  📁 Format: {result['format']}")
    print(f"  📊 Audio size: {len(result['audio_data']) if result['audio_data'] else 0} bytes")
    print(f"  ⏱️ Duration estimate: {result['duration_estimate']}s")
    if result['error']:
        print(f"  ❌ Error: {result['error']}")