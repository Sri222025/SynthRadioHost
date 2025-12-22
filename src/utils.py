"""
Utility functions for the application
"""
import re
from pathlib import Path
from datetime import datetime
from typing import Dict

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Convert text to safe filename
    
    Args:
        text: Input text
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def generate_output_filename(topic: str, audience: str, tone: str) -> str:
    """
    Generate output filename for audio
    
    Args:
        topic: Wikipedia topic
        audience: Target audience
        tone: Conversation tone
        
    Returns:
        Filename string
    """
    topic_clean = sanitize_filename(topic, max_length=30)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{topic_clean}_{audience}_{tone}_{timestamp}.mp3"

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2:34")
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def count_words(text: str) -> int:
    """
    Count words in text
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    return len(text.split())

def estimate_audio_duration(word_count: int, words_per_minute: int = 150) -> float:
    """
    Estimate audio duration from word count
    
    Args:
        word_count: Number of words
        words_per_minute: Speaking rate (default: 150 wpm for natural conversation)
        
    Returns:
        Estimated duration in seconds
    """
    return (word_count / words_per_minute) * 60

def save_script_to_file(script: str, output_path: Path) -> bool:
    """
    Save generated script to text file
    
    Args:
        script: Script content
        output_path: Output file path
        
    Returns:
        Success status
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script)
        
        return True
        
    except Exception as e:
        print(f"Error saving script: {e}")
        return False

def create_metadata_dict(
    topic: str,
    audience: str,
    tone: str,
    word_count: int,
    duration: float,
    script_path: str,
    audio_path: str
) -> Dict:
    """
    Create metadata dictionary for generated content
    
    Args:
        Various metadata fields
        
    Returns:
        Metadata dictionary
    """
    return {
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "word_count": word_count,
        "duration_seconds": duration,
        "duration_formatted": format_duration(duration),
        "script_path": script_path,
        "audio_path": audio_path,
        "generated_at": datetime.now().isoformat()
    }
