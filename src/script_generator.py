"""
LLM-based script generation using Google Gemini - PRODUCTION VERSION
"""
from google import genai
from google.genai import types
from typing import Optional, Dict, Any
from src.config import Config
from src.prompt_builder import build_script_prompt, validate_generated_script
import time

class ScriptGenerator:
    """Generate conversational scripts using Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError("❌ Gemini API key not found in secrets")
        
        print(f"✅ API Key loaded: {self.api_key[:15]}...")
        
        # Create client
        self.client = genai.Client(api_key=self.api_key)
        
        # USE STABLE MODEL with higher quota
        self.model_id = 'gemini-1.5-flash'
        
        print(f"✅ Using model: {self.model_id}")
    
    def generate_script(
        self, 
        topic: str, 
        tone: str, 
        audience: str, 
        wikipedia_content: str,
        retry_count: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Generate conversational script with smart retry logic"""
        
        prompt = build_script_prompt(topic, tone, audience, wikipedia_content)
        
        print(f"🎬 Starting script generation for {topic}/{audience}/{tone}")
        
        for attempt in range(retry_count + 1):
            try:
                # Add intelligent delay
                if attempt > 0:
                    wait_time = min(attempt * 10, 60)  # Cap at 60 seconds
                    print(f"⏰ Waiting {wait_time}s before retry {attempt + 1}...")
                    time.sleep(wait_time)
                
                print(f"📡 Attempt {attempt + 1}/{retry_count + 1} - Calling Gemini API...")
                
                # Generate content
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.9,
                        top_p=0.95,
                        top_k=40,
                        max_output_tokens=2048
                    )
                )
                
                if not response or not response.text:
                    print(f"⚠️ Empty response on attempt {attempt + 1}")
                    continue
                
                script = response.text.strip()
                print(f"✅ Received script ({len(script)} chars)")
                
                # Validate
                is_valid, issues = validate_generated_script(script, audience)
                
                if is_valid:
                    print(f"✅ Script validation PASSED!")
                    return {
                        "script": script,
                        "topic": topic,
                        "tone": tone,
                        "audience": audience,
                        "word_count": len(script.split()),
                        "validation_status": "passed",
                        "issues": [],
                        "attempt": attempt + 1
                    }
                else:
                    print(f"⚠️ Validation issues: {issues}")
                    
                    if attempt < retry_count:
                        prompt += f"\n\nPREVIOUS ATTEMPT HAD ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues)
                        prompt += "\n\nPlease fix these issues and regenerate."
                    else:
                        print(f"⚠️ Returning script with warnings")
                        return {
                            "script": script,
                            "topic": topic,
                            "tone": tone,
                            "audience": audience,
                            "word_count": len(script.split()),
                            "validation_status": "warning",
                            "issues": issues,
                            "attempt": attempt + 1
                        }
                        
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                
                print(f"❌ Error on attempt {attempt + 1}:")
                print(f"   Type: {error_type}")
                print(f"   Message: {error_msg[:200]}")
                
                # Handle rate limit specifically
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    if "retry in" in error_msg.lower():
                        # Extract retry delay from error
                        import re
                        match = re.search(r'retry in (\d+)', error_msg)
                        if match:
                            retry_delay = int(match.group(1)) + 5
                            print(f"⏰ Rate limit hit. Waiting {retry_delay}s as suggested...")
                            if attempt < retry_count:
                                time.sleep(retry_delay)
                                continue
                    
                    print(f"❌ QUOTA EXHAUSTED - You need a new API key!")
                    print(f"   Go to: https://aistudio.google.com/app/apikey")
                    print(f"   Create API key in NEW PROJECT")
                    return None
                
                # Handle model not found
                if "404" in error_msg or "NOT_FOUND" in error_msg:
                    print(f"❌ Model '{self.model_id}' not found!")
                    print(f"   Try switching to: gemini-1.5-flash or gemini-1.5-pro")
                    return None
                
                # Final attempt failed
                if attempt == retry_count:
                    print(f"❌ All {retry_count + 1} attempts failed")
                    return None
        
        return None
    
    def parse_script_by_speaker(self, script: str, audience: str) -> list:
        """Parse script into speaker segments"""
        from src.personas import get_persona
        
        male_persona = get_persona(audience, "male")
        female_persona = get_persona(audience, "female")
        
        male_name = male_persona['name']
        female_name = female_persona['name']
        
        segments = []
        lines = script.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith(male_name + ":"):
                dialogue = line.replace(male_name + ":", "").strip()
                segments.append({
                    "speaker": "male",
                    "speaker_name": male_name,
                    "dialogue": dialogue
                })
            elif line.startswith(female_name + ":"):
                dialogue = line.replace(female_name + ":", "").strip()
                segments.append({
                    "speaker": "female",
                    "speaker_name": female_name,
                    "dialogue": dialogue
                })
        
        return segments
