"""
Groq-based Script Generator for Hinglish 2-person conversations
With automatic retry and rate limit handling
"""

import json
import re
import requests
import time
from typing import Dict, List, Optional

class GroqScriptGenerator:
    """Generate Hinglish 2-person podcast scripts using Groq API"""
    
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
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = 5
    
    def _build_prompt(self, topic: str, wikipedia_content: str, duration_minutes: int, style: str, audience: str) -> str:
        profile = self.AUDIENCE_PROFILES.get(audience, self.AUDIENCE_PROFILES["Adults"])
        num_turns = duration_minutes * 3
        
        prompt = f"""Create a {duration_minutes}-minute Hinglish podcast for {audience}.

Topic: {topic}
Content: {wikipedia_content[:1500]}

Style Guide:
- {profile['tone']}
- Use: {profile['examples']}
- Mix 60% Hindi, 40% English naturally
- Add fillers: umm, toh, achha, *laughs*

Return JSON only:
{{
  "title": "Engaging Hinglish title",
  "dialogue": [
    {{"speaker": "Rajesh", "text": "Namaste! Aaj baat karenge..."}},
    {{"speaker": "Priya", "text": "Haan Rajesh, yeh topic interesting hai..."}}
  ]
}}

Create {num_turns}-{num_turns+1} exchanges. Natural conversation, not Wikipedia reading."""
        
        return prompt
    
    def generate_script(self, topic: str, wikipedia_content: str, duration_minutes: int = 2, style: str = "Conversational", audience: str = "Adults") -> Dict:
        prompt = self._build_prompt(topic, wikipedia_content, duration_minutes, style, audience)
        
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a Hinglish podcast writer. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 3000,
                    "top_p": 0.9
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 429:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "")
                    wait_time = self._extract_wait_time(error_msg)
                    
                    if attempt < self.max_retries - 1:
                        sleep_time = max(wait_time, (2 ** attempt))
                        time.sleep(sleep_time)
                        continue
                    else:
                        return {"success": False, "error": f"Rate limit exceeded. Please try again in {wait_time:.0f} seconds."}
                
                if response.status_code != 200:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return {"success": False, "error": f"API error {response.status_code}: {response.text}"}
                
                response_data = response.json()
                script_text = response_data["choices"][0]["message"]["content"].strip()
                
                script_data = self._extract_json(script_text)
                
                if not script_data:
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    return {"success": False, "error": "Failed to parse JSON from AI response"}
                
                if not self._validate_script(script_data):
                    if attempt < self.max_retries - 1:
                        time.sleep(1)
                        continue
                    return {"success": False, "error": "Invalid script structure"}
                
                return {"success": True, **script_data}
            
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": "Request timeout. Please try again."}
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": f"Error: {str(e)}"}
        
        return {"success": False, "error": "Failed after multiple retries. Please try again later."}
    
    def _extract_wait_time(self, error_message: str) -> float:
        try:
            match = re.search(r'(\d+(?:\.\d+)?)\s*(ms|s)', error_message.lower())
            if match:
                value = float(match.group(1))
                unit = match.group(2)
                if unit == 'ms':
                    return value / 1000
                return value
        except:
            pass
        return 1.0
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            
            return None
    
    def _validate_script(self, script_data: Dict) -> bool:
        if not isinstance(script_data, dict):
            return False
        
        if "dialogue" not in script_data:
            return False
        
        if not isinstance(script_data["dialogue"], list):
            return False
        
        if len(script_data["dialogue"]) < 2:
            return False
        
        for turn in script_data["dialogue"]:
            if not isinstance(turn, dict):
                return False
            if "speaker" not in turn or "text" not in turn:
                return False
        
        return True
