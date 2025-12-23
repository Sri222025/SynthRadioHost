# src/script_generator.py
"""
Script Generator with Audience Adaptation + Smart Retry
Generates audience-specific podcast scripts from Wikipedia content
"""

import os
import json
import google.generativeai as genai
from typing import Optional, Dict, List, Any
import re
import time

class ScriptGenerator:
    """Generates audience-adapted podcast scripts with smart retry logic"""
    
    # Audience profiles
    AUDIENCE_PROFILES = {
        "Kids (5-12)": {
            "vocabulary": "simple, everyday words",
            "sentence_length": "short and simple",
            "explanations": "use analogies with toys, games, and animals",
            "tone": "enthusiastic, fun, encouraging",
            "avoid": "complex terminology, abstract concepts",
            "include": "questions to keep engagement, exciting examples"
        },
        "Teenagers (13-18)": {
            "vocabulary": "modern, relatable language",
            "sentence_length": "moderate, conversational",
            "explanations": "use examples from social media, technology, pop culture",
            "tone": "casual, energetic, authentic",
            "avoid": "talking down, being too formal",
            "include": "real-world applications, current trends"
        },
        "Adults (19-60)": {
            "vocabulary": "professional, sophisticated",
            "sentence_length": "varied, well-structured",
            "explanations": "use practical examples, data, research",
            "tone": "informative, confident, respectful",
            "avoid": "oversimplification, condescension",
            "include": "facts, statistics, expert insights"
        },
        "Elderly (60+)": {
            "vocabulary": "clear, respectful language",
            "sentence_length": "moderate pace, well-paced",
            "explanations": "relate to life experience, historical context",
            "tone": "warm, patient, respectful",
            "avoid": "rushing, excessive jargon",
            "include": "historical connections, thoughtful reflections"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=self.api_key)
        
        # Use the model you have access to
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Optimized generation config for lower token usage
        self.generation_config = {
            'temperature': 0.8,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 4096,  # Reduced from 8192 to save quota
        }
        
        # Retry settings
        self.max_retries = 3
        self.retry_delay = 60  # Wait 60 seconds between retries for quota errors
    
    def _build_audience_prompt(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int,
        style: str,
        audience: str
    ) -> str:
        """Build audience-specific prompt - optimized for lower tokens"""
        
        profile = self.AUDIENCE_PROFILES.get(audience, self.AUDIENCE_PROFILES["Adults (19-60)"])
        approx_words = duration_minutes * 150
        
        # Limit Wikipedia content to reduce input tokens
        max_wiki_chars = 2500  # Reduced from 3000
        wiki_content_trimmed = wikipedia_content[:max_wiki_chars]
        if len(wikipedia_content) > max_wiki_chars:
            wiki_content_trimmed += "..."
        
        prompt = f"""Create a {duration_minutes}-minute podcast script for {audience} about "{topic_title}".

AUDIENCE: {audience}
- Vocabulary: {profile['vocabulary']}
- Tone: {profile['tone']}
- Explanations: {profile['explanations']}

STYLE: {style}
TARGET LENGTH: ~{approx_words} words

SOURCE (Wikipedia):
{wiki_content_trimmed}

OUTPUT (JSON only):
{{
  "title": "Catchy title",
  "description": "1-2 sentence description",
  "target_audience": "{audience}",
  "segments": [
    {{"speaker": "Host", "text": "Opening hook", "duration": 20, "type": "opening"}},
    {{"speaker": "Host", "text": "Main content", "duration": {duration_minutes * 40}, "type": "main"}},
    {{"speaker": "Host", "text": "Conclusion", "duration": 20, "type": "closing"}}
  ],
  "total_duration": {duration_minutes * 60},
  "key_adaptations": ["3-4 specific adaptations for {audience}"]
}}

Make it natural, engaging, and perfectly adapted for {audience}. Return ONLY valid JSON.
"""
        return prompt
    
    def generate_script(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int = 3,
        style: str = "Educational",
        audience: str = "Adults (19-60)"
    ) -> Dict[str, Any]:
        """
        Generate audience-adapted podcast script with smart retry
        
        Args:
            wikipedia_content: Content from Wikipedia article
            topic_title: Title of the Wikipedia topic
            duration_minutes: Target duration (1-10 minutes)
            style: Presentation style
            audience: Target audience segment
            
        Returns:
            Dict with success status and script data
        """
        try:
            if not wikipedia_content or not wikipedia_content.strip():
                return {
                    "success": False,
                    "error": "Wikipedia content is empty"
                }
            
            if not 1 <= duration_minutes <= 10:
                return {
                    "success": False,
                    "error": "Duration must be between 1 and 10 minutes"
                }
            
            # Build prompt
            prompt = self._build_audience_prompt(
                wikipedia_content,
                topic_title,
                duration_minutes,
                style,
                audience
            )
            
            # Try generating with retry logic
            for attempt in range(self.max_retries):
                try:
                    # Generate content
                    response = self.model.generate_content(
                        prompt,
                        generation_config=self.generation_config
                    )
                    
                    if not response.text:
                        return {
                            "success": False,
                            "error": "Content generation was blocked. Try a different topic."
                        }
                    
                    # Parse JSON
                    script_data = self._extract_json(response.text)
                    
                    if not script_data:
                        return {
                            "success": True,
                            "script": response.text,
                            "title": f"Podcast: {topic_title}",
                            "target_audience": audience,
                            "raw_response": True
                        }
                    
                    # Validate and return
                    validated_script = self._validate_script(script_data)
                    validated_script["target_audience"] = audience
                    validated_script["wikipedia_source"] = topic_title
                    
                    return {
                        "success": True,
                        **validated_script,
                        "script": response.text
                    }
                
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if it's a quota error
                    if "quota" in error_msg or "429" in error_msg or "resource_exhausted" in error_msg:
                        if attempt < self.max_retries - 1:
                            # Wait and retry
                            wait_time = self.retry_delay * (attempt + 1)
                            return {
                                "success": False,
                                "error": f"⏰ API quota limit reached. Please wait {wait_time} seconds and try again.",
                                "retry_after": wait_time,
                                "error_type": "quota_exceeded"
                            }
                        else:
                            return {
                                "success": False,
                                "error": "❌ API quota exhausted after multiple retries. Please try again in a few minutes or enable billing for higher limits.",
                                "error_type": "quota_exceeded"
                            }
                    else:
                        # Other error, don't retry
                        raise e
        
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific error types
            if "quota" in error_msg.lower() or "429" in error_msg or "resource_exhausted" in error_msg.lower():
                return {
                    "success": False,
                    "error": "⏰ API quota exceeded. Wait 60 seconds or enable billing at https://console.cloud.google.com/billing",
                    "error_type": "quota_exceeded"
                }
            elif "404" in error_msg or "not found" in error_msg.lower():
                return {
                    "success": False,
                    "error": "❌ Model not found. Your API key might not have access to gemini-2.0-flash-exp.",
                    "error_type": "model_not_found"
                }
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                return {
                    "success": False,
                    "error": "❌ Invalid API key. Please check your GEMINI_API_KEY.",
                    "error_type": "invalid_key"
                }
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                return {
                    "success": False,
                    "error": "❌ Network error. Please check your internet connection.",
                    "error_type": "network_error"
                }
            else:
                return {
                    "success": False,
                    "error": f"❌ Error: {error_msg}",
                    "error_type": type(e).__name__
                }
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from response"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try finding JSON object
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                return json.loads(text[start_idx:end_idx])
        except (json.JSONDecodeError, ValueError):
            pass
        
        return None
    
    def _validate_script(self, script_data: Dict) -> Dict[str, Any]:
        """Validate and clean script data"""
        validated = {
            "title": script_data.get("title", "Untitled Podcast"),
            "description": script_data.get("description", ""),
            "segments": [],
            "total_duration": script_data.get("total_duration", 180),
            "style": script_data.get("style", "Educational"),
            "key_adaptations": script_data.get("key_adaptations", [])
        }
        
        for seg in script_data.get("segments", []):
            if isinstance(seg, dict) and "text" in seg:
                validated_seg = {
                    "speaker": seg.get("speaker", "Host"),
                    "text": seg.get("text", "").strip(),
                    "duration": int(seg.get("duration", 30)),
                    "type": seg.get("type", "main"),
                    "notes": seg.get("notes", "")
                }
                if validated_seg["text"]:
                    validated["segments"].append(validated_seg)
        
        return validated


# Test function
if __name__ == "__main__":
    print("Testing ScriptGenerator...")
    print("-" * 60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        exit(1)
    
    print(f"✅ API Key: {api_key[:10]}...")
    
    try:
        generator = ScriptGenerator(api_key=api_key)
        print("✅ Generator initialized")
        
        # Test generation
        print("\nGenerating test script...")
        result = generator.generate_script(
            wikipedia_content="Artificial Intelligence is the simulation of human intelligence by machines.",
            topic_title="AI Basics",
            duration_minutes=2,
            style="Educational",
            audience="Adults (19-60)"
        )
        
        if result["success"]:
            print("✅ Script generated!")
            print(f"Title: {result.get('title')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
