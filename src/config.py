"""
Configuration management for Synthetic Radio Host
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent
    SAMPLES_DIR = BASE_DIR / "samples"
    PROMPTS_DIR = BASE_DIR / "prompts"
    TEMP_DIR = BASE_DIR / "temp"
    
    # API Keys - Read from Streamlit secrets or .env
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        ELEVENLABS_API_KEY = st.secrets.get("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY", ""))
    except:
        # Fallback to .env for local development
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Audio Settings
    DEFAULT_AUDIO_DURATION = int(os.getenv("DEFAULT_AUDIO_DURATION", 120))  # seconds
    TARGET_WORD_COUNT_MIN = 400
    TARGET_WORD_COUNT_MAX = 450
    AUDIO_SAMPLE_RATE = 24000
    AUDIO_BITRATE = "128k"
    
    # TTS Settings
    DEFAULT_TTS_ENGINE = os.getenv("DEFAULT_TTS_ENGINE", "bark")
    
    # Streamlit Settings
    STREAMLIT_TITLE = "🎙️ The Synthetic Radio Host"
    STREAMLIT_SUBTITLE = "Generate conversational Hinglish podcasts from Wikipedia"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.SAMPLES_DIR.mkdir(exist_ok=True)
        cls.PROMPTS_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)
        (cls.SAMPLES_DIR / "scripts").mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY not found in environment variables")
        
        return errors

# Create directories on import
Config.create_directories()
