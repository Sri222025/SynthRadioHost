# src/script_generator.py
"""
Script Generator with Audience Adaptation
Generates audience-specific podcast scripts from Wikipedia content
"""

import os
import json
import google.generativeai as genai
from typing import Optional, Dict, List, Any
import re

class ScriptGenerator:
    """Generates audience-adapted podcast scripts"""
    
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
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        self.generation_config = {
            'temperature': 0.8,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
    
    def _build_audience_prompt(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int,
        style: str,
        audience: str
    ) -> str:
        """Build audience-specific prompt"""
        
        profile = self.AUDIENCE_PROFILES.get(audience, self.AUDIENCE_PROFILES["Adults (19-60)"])
        approx_words = duration_minutes * 150
        
        prompt = f"""You are a professional podcast scriptwriter creating content for: {audience}

TOPIC: {topic_title}
DURATION: {duration_minutes} minutes (~{approx_words} words)
STYLE: {style}

TARGET AUDIENCE PROFILE:
- Vocabulary: {profile['vocabulary']}
- Sentence Structure: {profile['sentence_length']}
- Explanation Style: {profile['explanations']}
- Tone: {profile['tone']}
- Avoid: {profile['avoid']}
- Must Include: {profile['include']}

SOURCE CONTENT (Wikipedia):
{wikipedia_content[:3000]}

INSTRUCTIONS:
1. Adapt the Wikipedia content specifically for {audience}
2. Start with an engaging hook appropriate for this audience
3. Break down complex concepts using {profile['explanations']}
4. Use {profile['vocabulary']} throughout
5. Maintain {profile['tone']} tone consistently
6. Include smooth transitions between topics
7. End with a memorable, age-appropriate conclusion

SCRIPT STRUCTURE (JSON format):
{{
  "title": "Catchy, audience-appropriate title",
  "description": "Brief 1-2 sentence description",
  "target_audience": "{audience}",
  "segments": [
    {{
      "speaker": "Host",
      "text": "Opening hook - grab attention immediately",
      "duration": 20,
      "type": "opening",
      "notes": "Engagement strategy"
    }},
    {{
      "speaker": "Host",
      "text": "Main content explaining key concept #1",
      "duration": 100,
      "type": "main",
      "notes": "Simplified explanation with {profile['explanations']}"
    }},
    {{
      "speaker": "Host",
      "text": "Main content explaining key concept #2",
      "duration": 100,
      "type": "main",
      "notes": "Building on previous concept"
    }},
    {{
      "speaker": "Host",
      "text": "Conclusion with key takeaways",
      "duration": 20,
      "type": "closing",
      "notes": "Memorable ending"
    }}
  ],
  "total_duration": {duration_minutes * 60},
  "style": "{style}",
  "key_adaptations": ["List 3-4 specific ways you adapted content for {audience}"]
}}

CRITICAL: Return ONLY valid JSON. Ensure all text is natural, engaging, and perfectly adapted for {audience}.
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
        Generate audience-adapted podcast script
        
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
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "429" in error_msg:
                error_msg = "API quota exceeded. Please wait a minute and try again."
            elif "404" in error_msg:
                error_msg = "Model not found. Please check your API configuration."
            
            return {
                "success": False,
                "error": error_msg,
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
