"""
Synthetic Radio Host - Core Package
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Generate conversational Hinglish podcasts from Wikipedia"

from src.config import Config
from src.wikipedia_fetcher import WikipediaFetcher
from src.script_generator import ScriptGenerator
from src.tts_engine import TTSEngine
from src.audio_processor import AudioProcessor

__all__ = [
    'Config',
    'WikipediaFetcher',
    'ScriptGenerator',
    'TTSEngine',
    'AudioProcessor'
]
