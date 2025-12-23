"""
Mock TTS Engine for Streamlit Cloud deployment
Generates silent audio files for demonstration
"""
from pathlib import Path
from typing import List
import wave
import struct

class TTSEngine:
    """Mock TTS Engine - generates silent placeholder audio"""
    
    def __init__(self, engine: str = "mock"):
        self.engine = engine
        self.sample_rate = 24000
        print("⚠️ Using MOCK TTS Engine (silent audio for demo)")
    
    def generate_dialogue_segment(
        self,
        dialogue: str,
        speaker: str,
        audience: str,
        output_path: Path
    ) -> bool:
        """Generate mock silent audio"""
        try:
            # Estimate duration based on word count (150 words/min)
            words = len(dialogue.split())
            duration_seconds = (words / 150) * 60
            duration_seconds = max(2, min(duration_seconds, 10))  # 2-10 seconds
            
            # Generate silent audio
            num_samples = int(duration_seconds * self.sample_rate)
            
            # Create parent directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write WAV file
            with wave.open(str(output_path), 'wb') as wav:
                wav.setnchannels(1)  # Mono
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(self.sample_rate)
                # Write silent audio (all zeros)
                silent_data = struct.pack('h' * num_samples, *([0] * num_samples))
                wav.writeframes(silent_data)
            
            return True
            
        except Exception as e:
            print(f"Mock TTS error: {e}")
            return False
    
    def generate_full_conversation(
        self,
        segments: List[dict],
        audience: str,
        output_dir: Path
    ) -> List[Path]:
        """Generate mock audio for all segments"""
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_files = []
        
        for i, segment in enumerate(segments):
            output_path = output_dir / f"segment_{i:03d}_{segment['speaker']}.wav"
            
            success = self.generate_dialogue_segment(
                dialogue=segment['dialogue'],
                speaker=segment['speaker'],
                audience=audience,
                output_path=output_path
            )
            
            if success:
                audio_files.append(output_path)
                print(f"✅ Generated mock segment {i+1}/{len(segments)}")
            else:
                print(f"❌ Failed segment {i+1}")
        
        return audio_files
