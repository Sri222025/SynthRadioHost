# src/tts_engine_mock.py
"""
Mock TTS engine for development/testing when Vani TTS is not available
"""
import numpy as np
from scipy.io import wavfile
import os

class MockTTSEngine:
    """Mock TTS engine that generates silence"""
    
    def __init__(self):
        self.sample_rate = 22050
        
    def generate_speech(self, text: str, voice: str = "default") -> bytes:
        """
        Generate mock audio (silence) for testing
        Returns WAV format audio bytes
        """
        # Generate 2 seconds of silence per 100 characters
        duration = max(2.0, len(text) / 50)
        num_samples = int(self.sample_rate * duration)
        
        # Create silent audio
        audio_data = np.zeros(num_samples, dtype=np.int16)
        
        # Convert to WAV bytes
        import io
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        
        return buffer.read()
    
    def synthesize(self, text: str, output_path: str, voice: str = "default") -> str:
        """
        Generate speech and save to file
        Returns the output path
        """
        audio_bytes = self.generate_speech(text, voice)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
            
        return output_path
