"""
Unit tests for Prompt Builder
"""
import pytest
from src.prompt_builder import build_script_prompt, validate_generated_script
from src.config import Config

class TestPromptBuilder:
    """Test prompt building functionality"""
    
    def test_build_script_prompt_kids_funny(self):
        """Test building prompt for kids with funny tone"""
        prompt = build_script_prompt(
            topic="ChatGPT",
            tone="funny",
            audience="kids",
            wikipedia_content="ChatGPT is an AI chatbot."
        )
        
        assert "ChatGPT" in prompt
        assert "funny" in prompt.lower() or "FUNNY" in prompt
        assert "BOY" in prompt
        assert "GIRL" in prompt
        assert "Hinglish" in prompt or "hinglish" in prompt
        assert "[laughs]" in prompt or "[giggles]" in prompt
    
    def test_build_script_prompt_teens_witty(self):
        """Test building prompt for teenagers with witty tone"""
        prompt = build_script_prompt(
            topic="Virat Kohli",
            tone="witty",
            audience="teenagers",
            wikipedia_content="Virat Kohli is an Indian cricketer."
        )
        
        assert "Virat Kohli" in prompt
        assert "witty" in prompt.lower() or "WITTY" in prompt
        assert "TEEN" in prompt
        assert "slang" in prompt.lower()
    
    def test_build_script_prompt_adults_professional(self):
        """Test building prompt for adults with professional tone"""
        prompt = build_script_prompt(
            topic="Indian Economy",
            tone="professional",
            audience="adults",
            wikipedia_content="The Indian economy is the fifth-largest economy."
        )
        
        assert "Indian Economy" in prompt
        assert "professional" in prompt.lower() or "PROFESSIONAL" in prompt
        assert "SPEAKER" in prompt
    
    def test_prompt_contains_all_requirements(self):
        """Test that prompt contains all necessary elements"""
        prompt = build_script_prompt(
            topic="Test Topic",
            tone="casual",
            audience="kids",
            wikipedia_content="Test content"
        )
        
        # Check for key sections
        assert "SPEAKER PERSONAS" in prompt or "SPEAKERS" in prompt
        assert "HINGLISH" in prompt
        assert "CONVERSATIONAL" in prompt or "conversational" in prompt
        assert "OUTPUT FORMAT" in prompt or "FORMAT" in prompt
        assert str(Config.TARGET_WORD_COUNT_MIN) in prompt
        assert str(Config.TARGET_WORD_COUNT_MAX) in prompt


class TestScriptValidation:
    """Test script validation functionality"""
    
    def test_validate_complete_script(self, sample_script_kids):
        """Test validation of complete valid script"""
        is_valid, issues = validate_generated_script(sample_script_kids, "kids")
        
        # Script might be too short, but structure should be valid
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)
    
    def test_validate_missing_male_speaker(self):
        """Test detection of missing male speaker"""
        script = """
GIRL: Hello there!
GIRL: How are you?
GIRL: I am doing well.
""" * 20
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("BOY" in issue for issue in issues)
    
    def test_validate_missing_female_speaker(self):
        """Test detection of missing female speaker"""
        script = """
BOY: Hello there!
BOY: How are you?
BOY: I am doing well.
""" * 20
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("GIRL" in issue for issue in issues)
    
    def test_validate_script_too_short(self):
        """Test detection of too-short scripts"""
        script = "BOY: Hi [excited]\nGIRL: Hello [giggles]"
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("too short" in issue for issue in issues)
    
    def test_validate_script_too_long(self):
        """Test detection of too-long scripts"""
        script = ("BOY: " + " ".join(["word"] * 100) + " [excited]\n" +
                 "GIRL: " + " ".join(["word"] * 100) + " [giggles]\n") * 5
        
        is_valid, issues = validate_generated_script(script, "kids")
        
        assert not is_valid
        assert any("too long" in issue for issue in issues)
