"""
Audio processing: merging, effects, and export
"""
from pathlib import Path
from typing import List
from pydub import AudioSegment
from pydub.effects import normalize
from src.config import Config

class AudioProcessor:
    """Process and merge audio files"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.sample_rate = Config.AUDIO_SAMPLE_RATE
        self.bitrate = Config.AUDIO_BITRATE
    
    def load_audio(self, file_path: Path) -> AudioSegment:
        """
        Load audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            AudioSegment object
        """
        return AudioSegment.from_wav(str(file_path))
    
    def add_pause(self, duration_ms: int = 500) -> AudioSegment:
        """
        Create silence/pause
        
        Args:
            duration_ms: Pause duration in milliseconds
            
        Returns:
            Silent AudioSegment
        """
        return AudioSegment.silent(duration=duration_ms)
    
    def merge_segments(
        self, 
        audio_files: List[Path], 
        pause_duration: int = 500
    ) -> AudioSegment:
        """
        Merge multiple audio segments with pauses
        
        Args:
            audio_files: List of audio file paths
            pause_duration: Pause between segments in ms
            
        Returns:
            Merged AudioSegment
        """
        if not audio_files:
            raise ValueError("No audio files provided")
        
        # Load first file
        merged = self.load_audio(audio_files[0])
        pause = self.add_pause(pause_duration)
        
        # Add remaining files with pauses
        for audio_file in audio_files[1:]:
            audio = self.load_audio(audio_file)
            merged = merged + pause + audio
        
        return merged
    
    def normalize_audio(self, audio: AudioSegment) -> AudioSegment:
        """
        Normalize audio volume
        
        Args:
            audio: AudioSegment to normalize
            
        Returns:
            Normalized AudioSegment
        """
        return normalize(audio)
    
    def export_mp3(
        self, 
        audio: AudioSegment, 
        output_path: Path,
        normalize_volume: bool = True
    ) -> bool:
        """
        Export audio as MP3
        
        Args:
            audio: AudioSegment to export
            output_path: Output MP3 file path
            normalize_volume: Whether to normalize volume
            
        Returns:
            Success status
        """
        try:
            # Normalize if requested
            if normalize_volume:
                audio = self.normalize_audio(audio)
            
            # Export as MP3
            audio.export(
                str(output_path),
                format="mp3",
                bitrate=self.bitrate
            )
            
            print(f"✅ Exported: {output_path}")
            print(f"   Duration: {len(audio) / 1000:.1f} seconds")
            print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def process_conversation(
        self,
        audio_files: List[Path],
        output_path: Path,
        pause_duration: int = 500
    ) -> bool:
        """
        Complete processing pipeline: merge + normalize + export
        
        Args:
            audio_files: List of audio segment files
            output_path: Final MP3 output path
            pause_duration: Pause between segments in ms
            
        Returns:
            Success status
        """
        try:
            print(f"🎵 Processing {len(audio_files)} audio segments...")
            
            # Merge segments
            merged = self.merge_segments(audio_files, pause_duration)
            
            # Export
            success = self.export_mp3(merged, output_path)
            
            return success
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            return False
    
    def get_audio_duration(self, file_path: Path) -> float:
        """
        Get audio file duration in seconds
        
        Args:
            file_path: Audio file path
            
        Returns:
            Duration in seconds
        """
        audio = self.load_audio(file_path)
        return len(audio) / 1000


# Example usage
if __name__ == "__main__":
    processor = AudioProcessor()
    
    # Test with sample files (you'll need actual audio files)
    # audio_files = [
    #     Config.TEMP_DIR / "segment_001.wav",
    #     Config.TEMP_DIR / "segment_002.wav"
    # ]
    
    # output_path = Config.SAMPLES_DIR / "test_output.mp3"
    
    # success = processor.process_conversation(
    #     audio_files=audio_files,
    #     output_path=output_path
    # )
    
    print("Audio processor module ready")
