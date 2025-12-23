# src/tts_engine_mock.py
"""Mock TTS engine for testing"""
import numpy as np
from scipy.io import wavfile
import os
import io

class MockTTSEngine:
    """Mock TTS engine that generates silence"""
    
    def __init__(self):
        self.sample_rate = 22050
        
    def generate_speech(self, text: str, voice: str = "default") -> bytes:
        """Generate mock audio (silence) for testing"""
        duration = max(2.0, len(text) / 50)
        num_samples = int(self.sample_rate * duration)
        audio_data = np.zeros(num_samples, dtype=np.int16)
        
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_data)
        buffer.seek(0)
        return buffer.read()
    
    def synthesize(self, text: str, output_path: str, voice: str = "default") -> str:
        """Generate speech and save to file"""
        audio_bytes = self.generate_speech(text, voice)
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
        return output_path
