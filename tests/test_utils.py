"""
Unit tests for utility functions
"""
import pytest
from pathlib import Path
from src.utils import (
    sanitize_filename,
    generate_output_filename,
    format_duration,
    count_words,
    estimate_audio_duration,
    save_script_to_file,
    create_metadata_dict
)

class TestFilenameUtils:
    """Test filename utility functions"""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization"""
        result = sanitize_filename("Hello World")
        
        assert result == "hello_world"
    
    def test_sanitize_filename_special_chars(self):
        """Test sanitization removes special characters"""
        result = sanitize_filename("Hello@World! #Test")
        
        assert "@" not in result
        assert "!" not in result
        assert "#" not in result
    
    def test_sanitize_filename_long_text(self):
        """Test truncation of long filenames"""
        long_text = "a" * 100
        result = sanitize_filename(long_text, max_length=50)
        
        assert len(result) == 50
    
    def test_generate_output_filename(self):
        """Test output filename generation"""
        filename = generate_output_filename("ChatGPT", "kids", "funny")
        
        assert "chatgpt" in filename.lower()
        assert "kids" in filename
        assert "funny" in filename
        assert filename.endswith(".mp3")


class TestDurationUtils:
    """Test duration utility functions"""
    
    def test_format_duration_seconds(self):
        """Test formatting duration under 1 minute"""
        result = format_duration(45.5)
        
        assert result == "0:45"
    
    def test_format_duration_minutes(self):
        """Test formatting duration in minutes"""
        result = format_duration(125.0)
        
        assert result == "2:05"
    
    def test_format_duration_zero(self):
        """Test formatting zero duration"""
        result = format_duration(0)
        
        assert result == "0:00"


class TestTextUtils:
    """Test text utility functions"""
    
    def test_count_words_simple(self):
        """Test word counting"""
        text = "Hello world this is a test"
        count = count_words(text)
        
        assert count == 6
    
    def test_count_words_empty(self):
        """Test counting words in empty string"""
        count = count_words("")
        
        assert count == 1  # split() returns ['']
    
    def test_estimate_audio_duration(self):
        """Test audio duration estimation"""
        duration = estimate_audio_duration(450, words_per_minute=150)
        
        # 450 words at 150 wpm = 3 minutes = 180 seconds
        assert duration == pytest.approx(180.0, rel=0.01)


class TestFileOperations:
    """Test file operation utilities"""
    
    def test_save_script_to_file(self, temp_test_dir):
        """Test saving script to file"""
        script = "This is a test script\nWith multiple lines"
        output_path = temp_test_dir / "test_script.txt"
        
        success = save_script_to_file(script, output_path)
        
        assert success
        assert output_path.exists()
        
        # Verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == script
    
    def test_save_script_creates_directory(self, temp_test_dir):
        """Test that saving script creates parent directories"""
        script = "Test script"
        output_path = temp_test_dir / "subdir" / "test_script.txt"
        
        success = save_script_to_file(script, output_path)
        
        assert success
        assert output_path.exists()


class TestMetadata:
    """Test metadata creation"""
    
    def test_create_metadata_dict(self):
        """Test creating metadata dictionary"""
        metadata = create_metadata_dict(
            topic="ChatGPT",
            audience="kids",
            tone="funny",
            word_count=450,
            duration=120.5,
            script_path="/path/to/script.txt",
            audio_path="/path/to/audio.mp3"
        )
        
        assert metadata["topic"] == "ChatGPT"
        assert metadata["audience"] == "kids"
        assert metadata["tone"] == "funny"
        assert metadata["word_count"] == 450
        assert metadata["duration_seconds"] == 120.5
        assert "duration_formatted" in metadata
        assert "generated_at" in metadata
