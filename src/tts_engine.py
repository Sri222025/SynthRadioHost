"""
Text-to-Speech engine supporting Bark and ElevenLabs
"""
import os
from pathlib import Path
from typing import Optional, List
import numpy as np
from scipy.io import wavfile
from src.config import Config
from src.personas import get_persona

class TTSEngine:
    """Text-to-Speech conversion using Bark or ElevenLabs"""
    
    def __init__(self, engine: str = "bark"):
        """
        Initialize TTS engine
        
        Args:
            engine: "bark" or "elevenlabs"
        """
        self.engine = engine.lower()
        
        if self.engine == "bark":
            self._init_bark()
        elif self.engine == "elevenlabs":
            self._init_elevenlabs()
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")
    
    def _init_bark(self):
        """Initialize Bark TTS"""
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            
            self.bark_generate = generate_audio
            self.bark_sample_rate = SAMPLE_RATE
            
            # Preload models for faster generation
            print("Loading Bark models... (this may take a moment)")
            preload_models()
            print("✅ Bark models loaded")
            
        except ImportError:
            raise ImportError("Bark not installed. Run: pip install bark")
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS"""
        try:
            from elevenlabs import set_api_key, generate, voices
            
            api_key = Config.ELEVENLABS_API_KEY
            
            if not api_key:
                raise ValueError("ElevenLabs API key not found in .env")
            
            set_api_key(api_key)
            self.elevenlabs_generate = generate
            self.elevenlabs_voices = voices
            
            print("✅ ElevenLabs initialized")
            
        except ImportError:
            raise ImportError("ElevenLabs not installed. Run: pip install elevenlabs")
    
    def generate_speech_bark(
        self, 
        text: str, 
        voice_preset: str, 
        output_path: Path
    ) -> bool:
        """
        Generate speech using Bark
        
        Args:
            text: Text to convert
            voice_preset: Bark voice preset (e.g., "v2/en_speaker_6")
            output_path: Output WAV file path
            
        Returns:
            Success status
        """
        try:
            # Generate audio
            audio_array = self.bark_generate(
                text,
                history_prompt=voice_preset
            )
            
            # Save to file
            wavfile.write(
                str(output_path),
                self.bark_sample_rate,
                audio_array
            )
            
            return True
            
        except Exception as e:
            print(f"Bark generation error: {e}")
            return False
    
    def generate_speech_elevenlabs(
        self, 
        text: str, 
        voice_name: str, 
        output_path: Path
    ) -> bool:
        """
        Generate speech using ElevenLabs
        
        Args:
            text: Text to convert
            voice_name: ElevenLabs voice name
            output_path: Output MP3 file path
            
        Returns:
            Success status
        """
        try:
            # Generate audio
            audio = self.elevenlabs_generate(
                text=text,
                voice=voice_name
            )
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(audio)
            
            return True
            
        except Exception as e:
            print(f"ElevenLabs generation error: {e}")
            return False
    
    def generate_dialogue_segment(
        self,
        dialogue: str,
        speaker: str,
        audience: str,
        output_path: Path
    ) -> bool:
        """
        Generate audio for a single dialogue segment
        
        Args:
            dialogue: Dialogue text
            speaker: "male" or "female"
            audience: Target audience
            output_path: Output file path
            
        Returns:
            Success status
        """
        persona = get_persona(audience, speaker)
        
        if self.engine == "bark":
            voice_preset = persona['bark_voice']
            return self.generate_speech_bark(dialogue, voice_preset, output_path)
        
        elif self.engine == "elevenlabs":
            voice_name = persona['elevenlabs_voice']
            return self.generate_speech_elevenlabs(dialogue, voice_name, output_path)
        
        return False
    
    def generate_full_conversation(
        self,
        segments: List[dict],
        audience: str,
        output_dir: Path
    ) -> List[Path]:
        """
        Generate audio files for all conversation segments
        
        Args:
            segments: List of segment dictionaries from script parser
            audience: Target audience
            output_dir: Directory to save audio files
            
        Returns:
            List of generated audio file paths
        """
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
                print(f"✅ Generated segment {i+1}/{len(segments)}")
            else:
                print(f"❌ Failed to generate segment {i+1}")
        
        return audio_files


# Example usage
if __name__ == "__main__":
    # Test Bark TTS
    tts = TTSEngine(engine="bark")
    
    test_segments = [
        {
            "speaker": "male",
            "speaker_name": "BOY",
            "dialogue": "Arey yaar, ChatGPT ke baare mein suna hai? [excited]"
        },
        {
            "speaker": "female",
            "speaker_name": "GIRL",
            "dialogue": "Haan! Wo toh bahut cool hai! [giggles]"
        }
    ]
    
    output_dir = Config.TEMP_DIR / "test_audio"
    
    audio_files = tts.generate_full_conversation(
        segments=test_segments,
        audience="kids",
        output_dir=output_dir
    )
    
    print(f"\n✅ Generated {len(audio_files)} audio files")
    for file in audio_files:
        print(f"  - {file}")
