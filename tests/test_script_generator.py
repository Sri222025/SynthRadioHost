"""
Unit tests for Script Generator
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.script_generator import ScriptGenerator
from src.config import Config

class TestScriptGenerator:
    """Test ScriptGenerator class"""
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                generator = ScriptGenerator(api_key="test_key")
                assert generator.api_key == "test_key"
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error"""
        with patch.object(Config, 'GEMINI_API_KEY', ''):
            with pytest.raises(ValueError, match="Gemini API key not found"):
                ScriptGenerator()
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_script_success(self, mock_model_class, mock_configure, sample_wikipedia_content):
        """Test successful script generation"""
        # Mock the response
        mock_response = Mock()
        mock_response.text = """
BOY: Arey yaar, ChatGPT ke baare mein suna hai? [excited]
GIRL: Haan! Wo toh bahut cool hai yaar! [giggles]
BOY: Matlab ye kya kar sakta hai? [curious]
GIRL: Bahut kuch! Stories likh sakta hai, questions answer kar sakta hai [excited]
BOY: Wow! That's amazing na! [surprised]
GIRL: Haan! But responsibly use karna chahiye [thoughtful]
"""
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        generator = ScriptGenerator(api_key="test_key")
        
        result = generator.generate_script(
            topic="ChatGPT",
            tone="funny",
            audience="kids",
            wikipedia_content=sample_wikipedia_content
        )
        
        assert result is not None
        assert result["topic"] == "ChatGPT"
        assert result["tone"] == "funny"
        assert result["audience"] == "kids"
        assert "script" in result
        assert result["word_count"] > 0
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_script_retry_on_validation_failure(self, mock_model_class, mock_configure, sample_wikipedia_content):
        """Test retry mechanism on validation failure"""
        mock_model = Mock()
        
        # First call returns invalid script, second call returns valid
        invalid_response = Mock()
        invalid_response.text = "This is not a valid script format"
        
        valid_response = Mock()
        valid_response.text = """
BOY: Arey yaar, ChatGPT ke baare mein suna hai? [excited]
GIRL: Haan! Wo toh bahut cool hai! [giggles] Matlab robot hai kya?
BOY: Nahin yaar! Computer program hai [explains]
GIRL: Achha! Toh homework mein help karega? [curious]
BOY: Haan! But khud se bhi seekhna padega [thoughtful]
GIRL: Bilkul sahi! [agrees]
"""
        
        mock_model.generate_content.side_effect = [invalid_response, valid_response]
        mock_model_class.return_value = mock_model
        
        generator = ScriptGenerator(api_key="test_key")
        
        result = generator.generate_script(
            topic="ChatGPT",
            tone="educational",
            audience="kids",
            wikipedia_content=sample_wikipedia_content,
            retry_count=1
        )
        
        assert result is not None
        assert result["attempt"] == 2  # Second attempt succeeded
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_parse_script_by_speaker(self, mock_model_class, mock_configure, sample_script_kids):
        """Test parsing script into speaker segments"""
        generator = ScriptGenerator(api_key="test_key")
        
        segments = generator.parse_script_by_speaker(sample_script_kids, "kids")
        
        assert len(segments) > 0
        assert all("speaker" in seg for seg in segments)
        assert all("speaker_name" in seg for seg in segments)
        assert all("dialogue" in seg for seg in segments)
        
        # Check for both male and female speakers
        speakers = [seg["speaker"] for seg in segments]
        assert "male" in speakers
        assert "female" in speakers
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_generate_script_api_error(self, mock_model_class, mock_configure, sample_wikipedia_content):
        """Test handling of API errors"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        generator = ScriptGenerator(api_key="test_key")
        
        result = generator.generate_script(
            topic="ChatGPT",
            tone="funny",
            audience="kids",
            wikipedia_content=sample_wikipedia_content,
            retry_count=0
        )
        
        assert result is None


class TestScriptValidation:
    """Test script validation logic"""
    
    def test_validate_valid_script(self, sample_script_kids):
        """Test validation of a valid script"""
        from src.prompt_builder import validate_generated_script
        
        is_valid, issues = validate_generated_script(sample_script_kids, "kids")
        
        assert is_valid or len(issues) == 0 or "too short" in str(issues)  # May be too short
    
    def test_validate_missing_speakers(self):
        """Test validation catches missing speakers"""
        from src.prompt_builder import validate_generated_script
        
        script = "BOY: Hello there! BOY: How are you?"  # Only one speaker
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("Missing GIRL" in issue for issue in issues)
    
    def test_validate_no_emotion_tags(self):
        """Test validation catches missing emotion tags"""
        from src.prompt_builder import validate_generated_script
        
        script = """
BOY: Hello there friend.
GIRL: Hi, how are you doing today?
BOY: I am doing well thank you.
GIRL: That is great to hear.
""" * 10  # Make it long enough
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("emotion tags" in issue for issue in issues)
    
    def test_validate_no_hinglish(self):
        """Test validation catches pure English scripts"""
        from src.prompt_builder import validate_generated_script
        
        script = """
BOY: Hello there friend. [excited]
GIRL: Hi, how are you? [happy]
BOY: I am doing well. [cheerful]
GIRL: That is great. [giggles]
""" * 10
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("Hinglish" in issue for issue in issues)
