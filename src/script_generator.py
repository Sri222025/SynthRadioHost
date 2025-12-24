# src/script_generator.py
"""
Hinglish 2-Person Conversation Script Generator
Generates natural, conversational Hinglish dialogues with audience adaptation
"""

import os
import json
import re
from groq import Groq
from typing import Optional, Dict, List, Any

class ScriptGenerator:
    """Generates Hinglish 2-person podcast scripts using Groq"""
    
    AUDIENCE_PROFILES = {
        "Kids (5-12)": {
            "hindi_ratio": "30% Hindi, 70% English",
            "vocabulary": "simple words, cricket terms in English",
            "explanations": "compare to games, toys, cartoons",
            "expressions": "arre, wah, dekho, cool, nice",
            "tone": "excited, playful, encouraging"
        },
        "Teenagers (13-18)": {
            "hindi_ratio": "50% Hindi, 50% English",
            "vocabulary": "modern slang, social media terms",
            "explanations": "relate to Instagram, YouTube, trending topics",
            "expressions": "yaar, bro, literally, basically, matlab",
            "tone": "casual, energetic, relatable"
        },
        "Adults (19-60)": {
            "hindi_ratio": "60% Hindi, 40% English",
            "vocabulary": "professional mix, data, statistics",
            "explanations": "facts, figures, real-world examples",
            "expressions": "dekho, actually, bilkul, exactly, you know",
            "tone": "informative, balanced, conversational"
        },
        "Elderly (60+)": {
            "hindi_ratio": "70% Hindi, 30% English",
            "vocabulary": "clear Hindi, simple English",
            "explanations": "historical context, life experience",
            "expressions": "achha, theek hai, dekho, samajh rahe ho",
            "tone": "respectful, patient, warm"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq client"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def _build_hinglish_prompt(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int,
        style: str,
        audience: str,
        regenerate: bool = False
    ) -> str:
        """Build Hinglish 2-person conversation prompt"""
        
        profile = self.AUDIENCE_PROFILES.get(audience, self.AUDIENCE_PROFILES["Adults (19-60)"])
        approx_words = duration_minutes * 150
        
        # Limit Wikipedia content
        max_chars = 3000
        wiki_trimmed = wikipedia_content[:max_chars]
        if len(wikipedia_content) > max_chars:
            wiki_trimmed += "..."
        
        # Add variety for regeneration
        variation_note = ""
        if regenerate:
            variation_note = "\nIMPORTANT: Generate a DIFFERENT conversation style than before. Use new examples, different Hindi-English mix patterns, and fresh reactions."
        
        prompt = f"""You are creating a natural 2-person Hinglish podcast conversation about "{topic_title}" for {audience}.

CRITICAL HINGLISH RULES:
1. Language Mix: Use {profile['hindi_ratio']} throughout
2. Code-Switching: Switch between Hindi/English MID-SENTENCE naturally
   Example: "Dekho yaar, actually this team ne bahut accha performance kiya in 2020"
3. Natural Expressions: Use {profile['expressions']}
4. Conversational Fillers: Add "umm", "toh", "basically", "like", "you know"
5. Reactions: Include *laughs*, *chuckles*, "arre!", "wah!", interruptions

CONVERSATION STRUCTURE:
- Host 1 (Rajesh): Male host, asks questions, curious, uses slightly more English
- Host 2 (Priya): Female host, explains, enthusiastic, uses balanced Hinglish

AUDIENCE: {audience}
- Vocabulary: {profile['vocabulary']}
- Explanations: {profile['explanations']}
- Tone: {profile['tone']}

STYLE: {style}
TARGET: {approx_words} words (~{duration_minutes} minutes when spoken)

SOURCE CONTENT (Wikipedia):
{wiki_trimmed}

{variation_note}

DIALOGUE FORMAT RULES:
1. Start with casual greeting in Hinglish
2. Each turn: 2-4 sentences max (keep it conversational!)
3. Include natural interruptions, reactions, laughter
4. End with memorable Hinglish closing

OUTPUT (JSON only, no other text):
{{
  "title": "Hinglish title mixing Hindi-English",
  "description": "Brief description in Hinglish",
  "target_audience": "{audience}",
  "dialogue": [
    {{
      "speaker": "Rajesh",
      "text": "Arre Priya, aaj baat karte hain... umm, this is so exciting yaar!",
      "duration": 5,
      "type": "opening"
    }},
    {{
      "speaker": "Priya", 
      "text": "Haan Rajesh! *laughs* Dekho, actually ye topic bahut interesting hai, you know...",
      "duration": 6,
      "type": "opening"
    }},
    {{
      "speaker": "Rajesh",
      "text": "Achha achha, toh basically... wait, can you explain that part?",
      "duration": 4,
      "type": "main"
    }},
    {{
      "speaker": "Priya",
      "text": "Bilkul! Toh dekho, the main point is... umm, let me tell you...",
      "duration": 8,
      "type": "main"
    }}
  ],
  "total_duration": {duration_minutes * 60},
  "language_mix": "{profile['hindi_ratio']}",
  "key_adaptations": [
    "Used {profile['expressions']} for natural Hinglish flow",
    "Adapted vocabulary to {audience}",
    "Included conversational reactions and fillers"
  ]
}}

Make it sound like two Indian friends casually discussing over chai! Natural, fun, engaging!"""
        
        return prompt
    
    def generate_script(
        self,
        wikipedia_content: str,
        topic_title: str,
        duration_minutes: int = 2,
        style: str = "Conversational",
        audience: str = "Adults (19-60)",
        regenerate: bool = False
    ) -> Dict[str, Any]:
        """Generate Hinglish 2-person conversation script"""
        
        try:
            if not wikipedia_content or not wikipedia_content.strip():
                return {"success": False, "error": "Wikipedia content is empty"}
            
            if not 1 <= duration_minutes <= 10:
                return {"success": False, "error": "Duration must be between 1 and 10 minutes"}
            
            # Build prompt
            prompt = self._build_hinglish_prompt(
                wikipedia_content,
                topic_title,
                duration_minutes,
                style,
                audience,
                regenerate
            )
            
            # Generate with Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating natural Hinglish conversations between two Indian hosts. You understand code-switching, Indian expressions, and conversational dynamics."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.9 if regenerate else 0.8,  # More variety for regeneration
                max_tokens=4096,
                top_p=0.95
            )
            
            response_text = chat_completion.choices[0].message.content
            
            if not response_text:
                return {"success": False, "error": "No response from Groq API"}
            
            # Parse JSON
            script_data = self._extract_json(response_text)
            
            if not script_data:
                return {
                    "success": True,
                    "script": response_text,
                    "title": f"Conversation: {topic_title}",
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
                "raw_script": response_text
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Script generation error: {str(e)}",
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
            "title": script_data.get("title", "Untitled Conversation"),
            "description": script_data.get("description", ""),
            "dialogue": [],
            "total_duration": script_data.get("total_duration", 120),
            "language_mix": script_data.get("language_mix", "50% Hindi, 50% English"),
            "key_adaptations": script_data.get("key_adaptations", [])
        }
        
        # Validate dialogue array
        for turn in script_data.get("dialogue", []):
            if isinstance(turn, dict) and "text" in turn:
                validated_turn = {
                    "speaker": turn.get("speaker", "Host"),
                    "text": turn.get("text", "").strip(),
                    "duration": int(turn.get("duration", 5)),
                    "type": turn.get("type", "main")
                }
                if validated_turn["text"]:
                    validated["dialogue"].append(validated_turn)
        
        return validated
