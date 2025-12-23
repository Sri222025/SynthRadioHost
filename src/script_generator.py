"""
LLM-based script generation using Google Gemini (NEW API)
"""
from google import genai
from google.genai import types
from typing import Optional, Dict, Any
from src.config import Config
from src.prompt_builder import build_script_prompt, validate_generated_script

class ScriptGenerator:
    """Generate conversational scripts using Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError("Gemini API key not found")
        
        # NEW API: Create client
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = 'gemini-1.5-flash-exp'
    
    def generate_script(
        self, 
        topic: str, 
        tone: str, 
        audience: str, 
        wikipedia_content: str,
        retry_count: int = 3
    ) -> Optional[Dict[str, Any]]:
        """Generate conversational script with rate limit handling"""
        
        import time
        
        prompt = build_script_prompt(topic, tone, audience, wikipedia_content)
        
        for attempt in range(retry_count + 1):
            try:
                # Add delay between attempts
                if attempt > 0:
                    wait_time = attempt * 5
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                
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
                    print(f"Empty response on attempt {attempt + 1}")
                    continue
                
                script = response.text.strip()
                
                # Validate
                is_valid, issues = validate_generated_script(script, audience)
                
                if is_valid:
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
                    print(f"Validation failed (attempt {attempt + 1}): {issues}")
                    
                    if attempt < retry_count:
                        prompt += f"\n\nPREVIOUS ATTEMPT HAD ISSUES:\n" + "\n".join(f"- {issue}" for issue in issues)
                        prompt += "\n\nPlease fix these issues and regenerate."
                    else:
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
                print(f"Error (attempt {attempt + 1}): {error_msg}")
                
                # Check if rate limit error
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    if attempt < retry_count:
                        wait_time = (attempt + 1) * 10
                        print(f"⚠️ Rate limit hit. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print("❌ Rate limit exceeded after all retries")
                        return None
                
                if attempt == retry_count:
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
