"""
Unit tests for Audio Processor
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from pydub import AudioSegment
from src.audio_processor import AudioProcessor

class TestAudioProcessor:
    """Test AudioProcessor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = AudioProcessor()
    
    def test_init(self):
        """Test initialization"""
        assert self.processor is not None
        assert self.processor.sample_rate > 0
        assert self.processor.bitrate is not None
    
    def test_add_pause(self):
        """Test creating pause/silence"""
        pause = self.processor.add_pause(duration_ms=1000)
        
        assert isinstance(pause, AudioSegment)
        assert len(pause) == 1000  # 1 second
    
    @pytest.fixture
    def create_test_audio(self, temp_test_dir):
        """Create test audio files"""
        # Create simple audio segments
        audio1 = AudioSegment.silent(duration=1000)  # 1 second
        audio2 = AudioSegment.silent(duration=1000)
        
        file1 = temp_test_dir / "audio1.wav"
        file2 = temp_test_dir / "audio2.wav"
        
        audio1.export(str(file1), format="wav")
        audio2.export(str(file2), format="wav")
        
        return [file1, file2]
    
    def test_load_audio(self, create_test_audio):
        """Test loading audio file"""
        audio_files = create_test_audio
        
        audio = self.processor.load_audio(audio_files[0])
        
        assert isinstance(audio, AudioSegment)
        assert len(audio) > 0
    
    def test_merge_segments(self, create_test_audio):
        """Test merging audio segments"""
        audio_files = create_test_audio
        
        merged = self.processor.merge_segments(audio_files, pause_duration=500)
        
        assert isinstance(merged, AudioSegment)
        # Duration should be: audio1 + pause + audio2
        assert len(merged) >= 2500  # 1000 + 500 + 1000
    
    def test_merge_segments_empty_list(self):
        """Test merging with empty list raises error"""
        with pytest.raises(ValueError, match="No audio files provided"):
            self.processor.merge_segments([])
    
    def test_normalize_audio(self):
        """Test audio normalization"""
        audio = AudioSegment.silent(duration=1000)
        
        normalized = self.processor.normalize_audio(audio)
        
        assert isinstance(normalized, AudioSegment)
    
    def test_export_mp3(self, create_test_audio, temp_test_dir):
        """Test exporting audio as MP3"""
        audio_files = create_test_audio
        audio = self.processor.load_audio(audio_files[0])
        
        output_path = temp_test_dir / "output.mp3"
        
        success = self.processor.export_mp3(audio, output_path)
        
        assert success
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_process_conversation(self, create_test_audio, temp_test_dir):
        """Test complete conversation processing pipeline"""
        audio_files = create_test_audio
        output_path = temp_test_dir / "final_output.mp3"
        
        success = self.processor.process_conversation(
            audio_files=audio_files,
            output_path=output_path,
            pause_duration=500
        )
        
        assert success
        assert output_path.exists()
    
    def test_get_audio_duration(self, create_test_audio):
        """Test getting audio duration"""
        audio_files = create_test_audio
        
        duration = self.processor.get_audio_duration(audio_files[0])
        
        assert duration > 0
        assert duration == pytest.approx(1.0, rel=0.1)  # ~1 second


class TestAudioProcessorErrors:
    """Test error handling in AudioProcessor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = AudioProcessor()
    
    def test_load_audio_nonexistent_file(self):
        """Test loading non-existent file raises error"""
        with pytest.raises(Exception):
            self.processor.load_audio(Path("/nonexistent/file.wav"))
    
    def test_export_mp3_invalid_path(self):
        """Test exporting to invalid path"""
        audio = AudioSegment.silent(duration=1000)
        
        success = self.processor.export_mp3(
            audio,
            Path("/invalid/path/that/does/not/exist/output.mp3")
        )
        
        assert not success
