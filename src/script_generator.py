def generate_script(
    self, 
    topic: str, 
    tone: str, 
    audience: str, 
    wikipedia_content: str,
    retry_count: int = 3  # Increased retries
) -> Optional[Dict[str, any]]:
    """Generate conversational script with rate limit handling"""
    
    import time
    
    prompt = build_script_prompt(topic, tone, audience, wikipedia_content)
    
    for attempt in range(retry_count + 1):
        try:
            # Add delay between attempts to avoid rate limiting
            if attempt > 0:
                wait_time = attempt * 5  # 5, 10, 15 seconds
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            
            # NEW API: Generate content
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
            
            # Check if it's a rate limit error
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                if attempt < retry_count:
                    wait_time = (attempt + 1) * 10  # 10, 20, 30 seconds
                    print(f"⚠️ Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("❌ Rate limit exceeded after all retries")
                    return None
            
            if attempt == retry_count:
                return None
    
    return None
