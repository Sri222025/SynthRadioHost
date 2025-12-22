"""
Simple Audio Processor - NO EXTERNAL DEPENDENCIES
"""
from pathlib import Path
from typing import List
import wave
import struct

class AudioProcessor:
    """Simple audio processor"""
    
    def __init__(self):
        self.sample_rate = 24000
    
    def merge_segments(self, audio_files: List[Path], pause_duration: int = 500):
        """Merge WAV files"""
        merged = b''
        pause_frames = int((pause_duration / 1000) * self.sample_rate)
        pause = struct.pack('h' * pause_frames, *([0] * pause_frames))
        
        for i, f in enumerate(audio_files):
            with wave.open(str(f), 'rb') as w:
                merged += w.readframes(w.getnframes())
            if i < len(audio_files) - 1:
                merged += pause
        return merged
    
    def normalize_audio(self, audio):
        return audio
    
    def export_mp3(self, audio, output_path: Path, normalize_volume=True) -> bool:
        try:
            output_path = output_path.with_suffix('.wav')
            with wave.open(str(output_path), 'wb') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(self.sample_rate)
                w.writeframes(audio)
            print(f"✅ Saved: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def process_conversation(self, audio_files: List[Path], output_path: Path, pause_duration=500) -> bool:
        try:
            merged = self.merge_segments(audio_files, pause_duration)
            return self.export_mp3(merged, output_path)
        except:
            return False
    
    def get_audio_duration(self, file_path: Path) -> float:
        try:
            with wave.open(str(file_path), 'rb') as w:
                return w.getnframes() / float(w.getframerate())
        except:
            return 0.0
