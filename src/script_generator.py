# src/groq_script_generator.py
"""
Script Generator using Groq API (Llama 3.3 70B)
MUCH faster and higher quota than Gemini
"""

import os
import json
from groq import Groq
from typing import Optional, Dict, Any
import re

class GroqScriptGenerator:
    """Generates scripts using Groq's Llama models"""
    
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
        """Initialize Groq client"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=self.api_key)
        # Using Llama 3.3 70B - excellent for creative writing
        self.model = "llama-3.3-70b-versatile"
    
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
        
        # Limit content
        max_chars = 3000
        wiki_trimmed = wikipedia_content[:max_chars]
        if len(wikipedia_content) > max_chars:
            wiki_trimmed += "..."
        
        prompt = f"""You are an expert podcast scriptwriter. Create a {duration_minutes}-minute podcast script about "{topic_title}" for {audience}.

AUDIENCE PROFILE:
- Target: {audience}
- Vocabulary: {profile['vocabulary']}
- Tone: {profile['tone']}
- Explanation style: {profile['explanations']}
- Must avoid: {profile['avoid']}
- Must include: {profile['include']}

STYLE: {style}
TARGET LENGTH: Approximately {approx_words} words

SOURCE CONTENT (from Wikipedia):
{wiki_trimmed}

INSTRUCTIONS:
1. Adapt content specifically for {audience} - this is critical
2. Start with an attention-grabbing hook
3. Use {profile['explanations']}
4. Maintain {profile['tone']} throughout
5. Break into clear segments: opening, main content (2-3 key points), closing
6. Make it sound natural for audio
7. Include smooth transitions

OUTPUT FORMAT (respond with ONLY valid JSON):
{{
  "title": "Engaging, audience-appropriate title",
  "description": "Brief 1-2 sentence description",
  "target_audience": "{audience}",
  "segments": [
    {{
      "speaker": "Host",
      "text": "Opening segment - hook the listener immediately",
      "duration": 20,
      "type": "opening",
      "notes": "Attention-grabbing strategy used"
    }},
    {{
      "speaker": "Host",
      "text": "Main content segment 1 - first key concept",
      "duration": {duration_minutes * 20},
      "type": "main",
      "notes": "Adaptation approach for {audience}"
    }},
    {{
      "speaker": "Host",
      "text": "Main content segment 2 - second key concept",
      "duration": {duration_minutes * 20},
      "type": "main",
      "notes": "Connection to previous segment"
    }},
    {{
      "speaker": "Host",
      "text": "Closing segment - memorable takeaway",
      "duration": 20,
      "type": "closing",
      "notes": "Call to action or reflection"
    }}
  ],
  "total_duration": {duration_minutes * 60},
  "style": "{style}",
  "key_adaptations": ["List 3-4 specific ways you adapted this content for {audience}"]
}}

Return ONLY the JSON, no other text."""
        
        return prompt
    
    def generate_script(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int = 3,
        style: str = "Educational",
        audience: str = "Adults (19-60)"
    ) -> Dict[str, Any]:
        """Generate podcast script using Groq"""
        
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
            
            # Generate with Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert podcast scriptwriter who creates engaging, audience-adapted content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.8,
                max_tokens=4096,
                top_p=0.95
            )
            
            response_text = chat_completion.choices[0].message.content
            
            if not response_text:
                return {
                    "success": False,
                    "error": "No response from Groq API"
                }
            
            # Parse JSON
            script_data = self._extract_json(response_text)
            
            if not script_data:
                # If JSON parsing fails, return raw text
                return {
                    "success": True,
                    "script": response_text,
                    "title": f"Podcast: {topic_title}",
                    "target_audience": audience,
                    "raw_response": True
                }
            
            # Validate
            validated = self._validate_script(script_data)
            validated["target_audience"] = audience
            validated["wikipedia_source"] = topic_title
            
            return {
                "success": True,
                **validated,
                "script": response_text
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Groq API error: {str(e)}",
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
        """Validate script data"""
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
