"""
Groq-based Script Generator for Hinglish 2-person conversations
Uses direct HTTP API calls (no Groq client dependency issues)
"""

import json
import re
import requests
from typing import Dict, List, Optional

class GroqScriptGenerator:
    """Generate Hinglish 2-person podcast scripts using Groq API"""
    
    # Audience profiles for adaptation
    AUDIENCE_PROFILES = {
        "Kids": {
            "vocab": "Simple words, short sentences",
            "examples": "jaise, achha, dekho, suno",
            "tone": "Energetic, playful, lots of examples",
            "complexity": "Very basic concepts only"
        },
        "Teenagers": {
            "vocab": "Modern slang, trendy words",
            "examples": "matlab, basically, literally, cool hai",
            "tone": "Casual, relatable, fast-paced",
            "complexity": "Moderate depth with pop culture refs"
        },
        "Adults": {
            "vocab": "Professional yet conversational",
            "examples": "actually, technically, samajh rahe ho",
            "tone": "Informative but friendly",
            "complexity": "Detailed explanations with context"
        },
        "Elderly": {
            "vocab": "Clear, respectful, traditional",
            "examples": "aap samajh rahe hain, dhyaan se suniye",
            "tone": "Slow-paced, respectful, storytelling",
            "complexity": "Simple with life experience connections"
        }
    }
    
    def __init__(self, api_key: str):
        """Initialize with Groq API key"""
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def _build_prompt(
        self,
        topic: str,
        wikipedia_content: str,
        duration_minutes: int,
        style: str,
        audience: str
    ) -> str:
        """Build the Groq prompt for script generation"""
        
        profile = self.AUDIENCE_PROFILES.get(audience, self.AUDIENCE_PROFILES["Adults"])
        
        # Calculate approximate dialogue turns (each ~15-20 seconds)
        num_turns = duration_minutes * 3  # ~3-4 turns per minute
        
        prompt = f"""You are a professional Hinglish podcast script writer. Create a natural 2-person radio conversation.

**Topic:** {topic}

**Wikipedia Source Content:**
{wikipedia_content[:2000]}

**Target Audience:** {audience}
- Vocabulary: {profile['vocab']}
- Expression Examples: {profile['examples']}
- Tone: {profile['tone']}
- Complexity: {profile['complexity']}

**Conversation Requirements:**
1. **TWO SPEAKERS:** Rajesh (male host) and Priya (female co-host)
2. **Duration:** Approximately {duration_minutes} minutes ({num_turns}-{num_turns+2} dialogue turns)
3. **Language Style:** Natural Hinglish (60% Hindi, 40% English words mixed naturally)
4. **Conversational Elements:** Include natural fillers and interruptions:
   - Hindi fillers: "umm", "toh", "achha", "haan", "nahi", "arre", "matlab"
   - Reactions: "*laughs*", "*chuckles*", "*sighs*"
   - Interruptions: One speaker can gently interrupt/react to other
5. **Tone:** {style} style suitable for {audience}
6. **Content:** Based on Wikipedia facts, but make it conversational, not robotic

**Code-switching Rules:**
- Technical terms in English: "satellite", "technology", "mission"
- Common words in Hindi: "aur", "ke baad", "kya", "hai"
- Mix naturally: "ISRO ne launch kiya tha Chandrayaan mission"

**JSON OUTPUT FORMAT:**
{{
  "title": "Engaging podcast title in Hinglish",
  "description": "Brief 1-line description",
  "dialogue": [
    {{
      "speaker": "Rajesh",
      "text": "Namaste doston! *excited* Aaj hum baat karenge..."
    }},
    {{
      "speaker": "Priya",
      "text": "Haan Rajesh, aur yeh topic bahut interesting hai because..."
    }}
  ]
}}

**IMPORTANT:**
- Return ONLY valid JSON, no extra text
- Each dialogue turn should be 2-4 sentences
- Make it sound like real people talking, not reading Wikipedia
- Include {audience}-appropriate vocabulary and examples
- Total {num_turns}-{num_turns+2} dialogue exchanges

Generate the JSON now:"""
        
        return prompt
    
    def generate_script(
        self,
        topic: str,
        wikipedia_content: str,
        duration_minutes: int = 2,
        style: str = "Conversational",
        audience: str = "Adults"
    ) -> Dict:
        """Generate Hinglish podcast script using direct HTTP API"""
        
        try:
            # Build prompt
            prompt = self._build_prompt(
                topic, wikipedia_content, duration_minutes, style, audience
            )
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert Hinglish podcast script writer. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 4096,
                "top_p": 0.9
            }
            
            # Make API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Check for errors
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Groq API error {response.status_code}: {response.text}"
                }
            
            # Extract response
            response_data = response.json()
            script_text = response_data["choices"][0]["message"]["content"].strip()
            
            # Parse JSON
            script_data = self._extract_json(script_text)
            
            if not script_data:
                return {
                    "success": False,
                    "error": "Failed to parse JSON from AI response"
                }
            
            # Validate
            if not self._validate_script(script_data):
                return {
                    "success": False,
                    "error": "Invalid script structure"
                }
            
            return {
                "success": True,
                **script_data
            }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - Groq API took too long to respond"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from AI response (handles markdown code blocks)"""
        try:
            # Try direct parse first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting from code block
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try finding JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            return None
    
    def _validate_script(self, script_data: Dict) -> bool:
        """Validate script structure"""
        if not isinstance(script_data, dict):
            return False
        
        if "dialogue" not in script_data:
            return False
        
        if not isinstance(script_data["dialogue"], list):
            return False
        
        if len(script_data["dialogue"]) < 2:
            return False
        
        # Check each dialogue turn
        for turn in script_data["dialogue"]:
            if not isinstance(turn, dict):
                return False
            if "speaker" not in turn or "text" not in turn:
                return False
        
        return True
