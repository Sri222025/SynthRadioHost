# src/script_generator.py
"""
Script Generator Module
Generates podcast scripts using Google Gemini AI
"""

import os
import json
import google.generativeai as genai
from typing import Optional, Dict, List, Any
import re

class ScriptGenerator:
    """Generates podcast scripts using Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize with API key from parameter or environment
        
        Args:
            api_key: Optional API key. If not provided, reads from GEMINI_API_KEY env var
        
        Raises:
            ValueError: If no API key is found
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or parameters")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use the stable, available model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generation config for better consistency
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
    
    def _build_prompt(self, topic: str, duration_minutes: int, style: str) -> str:
        """
        Build a detailed prompt based on style
        
        Args:
            topic: The podcast topic
            duration_minutes: Target duration in minutes
            style: The style/tone (Informative, Conversational, Educational, Entertaining, News)
        
        Returns:
            Formatted prompt string
        """
        # Style-specific instructions
        style_guides = {
            "Informative": "Use a professional, fact-based tone. Focus on key information and insights. Include data and examples.",
            "Conversational": "Use a friendly, casual tone. Speak naturally as if talking to a friend. Include personal anecdotes and relatability.",
            "Educational": "Use a teaching tone. Break down complex concepts. Include explanations and step-by-step guidance.",
            "Entertaining": "Use humor, storytelling, and engaging narrative. Keep it fun and captivating. Include interesting facts and hooks.",
            "News": "Use a journalistic, objective tone. Present facts clearly. Include current context and implications."
        }
        
        style_guide = style_guides.get(style, style_guides["Informative"])
        
        # Calculate approximate word count (150 words per minute for speech)
        approx_words = duration_minutes * 150
        
        prompt = f"""You are a professional podcast scriptwriter. Create a {duration_minutes}-minute radio show script about: {topic}

STYLE REQUIREMENTS:
{style_guide}

STRUCTURE REQUIREMENTS:
1. Create an engaging opening (15-20% of time)
2. Develop main content with 2-3 key points (60-70% of time)
3. Include smooth transitions between segments
4. End with a memorable closing (10-15% of time)

TARGET: Approximately {approx_words} words total

FORMAT YOUR RESPONSE AS VALID JSON:
{{
  "title": "Catchy title for the show",
  "description": "Brief 1-2 sentence description",
  "segments": [
    {{
      "speaker": "Host",
      "text": "Full script text for this segment",
      "duration": 30,
      "type": "opening"
    }},
    {{
      "speaker": "Host", 
      "text": "Main content here",
      "duration": 180,
      "type": "main"
    }},
    {{
      "speaker": "Host",
      "text": "Closing remarks",
      "duration": 30,
      "type": "closing"
    }}
  ],
  "total_duration": {duration_minutes * 60},
  "style": "{style}"
}}

IMPORTANT: 
- Return ONLY the JSON, no other text
- Ensure all durations sum to approximately {duration_minutes * 60} seconds
- Make the script natural and engaging for audio
- Use conversational language that sounds good when spoken
"""
        return prompt
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        Extract JSON from response text, handling markdown code blocks
        
        Args:
            text: Raw response text that may contain JSON
        
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Try finding JSON object in text
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        return None
    
    def _validate_script(self, script_data: Dict) -> Dict[str, Any]:
        """
        Validate and clean script data
        
        Args:
            script_data: Raw script dictionary
        
        Returns:
            Validated and cleaned script dictionary
        """
        validated = {
            "title": script_data.get("title", "Untitled Podcast"),
            "description": script_data.get("description", ""),
            "segments": [],
            "total_duration": script_data.get("total_duration", 300),
            "style": script_data.get("style", "Informative")
        }
        
        # Validate segments
        for seg in script_data.get("segments", []):
            if isinstance(seg, dict) and "text" in seg:
                validated_seg = {
                    "speaker": seg.get("speaker", "Host"),
                    "text": seg.get("text", "").strip(),
                    "duration": int(seg.get("duration", 30)),
                    "type": seg.get("type", "main")
                }
                if validated_seg["text"]:  # Only include non-empty segments
                    validated["segments"].append(validated_seg)
        
        return validated
    
    def generate_script(
        self, 
        topic: str, 
        duration_minutes: int = 5,
        style: str = "Informative"
    ) -> Dict[str, Any]:
        """
        Generate podcast script
        
        Args:
            topic: The topic to create a podcast about
            duration_minutes: Target duration in minutes (1-30)
            style: Style/tone of the podcast
        
        Returns:
            Dictionary with 'success', 'script' (if successful), or 'error' (if failed)
        """
        try:
            # Validate inputs
            if not topic or not topic.strip():
                return {
                    "success": False,
                    "error": "Topic cannot be empty"
                }
            
            if not 1 <= duration_minutes <= 30:
                return {
                    "success": False,
                    "error": "Duration must be between 1 and 30 minutes"
                }
            
            # Build prompt
            prompt = self._build_prompt(topic, duration_minutes, style)
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Check for blocked content
            if not response.text:
                return {
                    "success": False,
                    "error": "Content generation was blocked. Try a different topic or rephrasing."
                }
            
            # Parse JSON from response
            script_data = self._extract_json(response.text)
            
            if not script_data:
                # If JSON parsing fails, return raw text
                return {
                    "success": True,
                    "script": response.text,
                    "title": f"Podcast: {topic}",
                    "raw_response": True
                }
            
            # Validate and clean the script
            validated_script = self._validate_script(script_data)
            
            # Return successful result with all data
            return {
                "success": True,
                **validated_script,
                "script": response.text  # Keep raw script for display
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific error types
            if "quota" in error_msg.lower() or "429" in error_msg:
                error_msg = "API quota exceeded. Please check your Gemini API billing and quota limits."
            elif "404" in error_msg or "not found" in error_msg.lower():
                error_msg = "Model not found. Please verify your API key has access to gemini-1.5-pro."
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                error_msg = "Invalid API key. Please check your GEMINI_API_KEY configuration."
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                error_msg = "Network error. Please check your internet connection."
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": type(e).__name__
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the API connection and model availability
        
        Returns:
            Dictionary with connection test results
        """
        try:
            response = self.model.generate_content(
                "Say 'API connection successful' in exactly those words.",
                generation_config={'max_output_tokens': 50}
            )
            
            return {
                "success": True,
                "message": "API connection successful",
                "response": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }


# Standalone test function
def test_script_generator():
    """Test function for debugging"""
    import sys
    
    print("Testing ScriptGenerator...")
    print("-" * 50)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize generator
        generator = ScriptGenerator(api_key=api_key)
        print("✅ ScriptGenerator initialized")
        
        # Test connection
        print("\nTesting API connection...")
        result = generator.test_connection()
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Connection failed: {result['error']}")
            sys.exit(1)
        
        # Generate test script
        print("\nGenerating test script...")
        script = generator.generate_script(
            topic="The Future of AI",
            duration_minutes=2,
            style="Informative"
        )
        
        if script["success"]:
            print("✅ Script generated successfully!")
            print(f"\nTitle: {script.get('title', 'N/A')}")
            print(f"Segments: {len(script.get('segments', []))}")
            print(f"\nFirst 200 chars of script:\n{script['script'][:200]}...")
        else:
            print(f"❌ Script generation failed: {script['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")


if __name__ == "__main__":
    test_script_generator()
