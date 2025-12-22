"""
Dynamic prompt generation for LLM based on audience and tone
"""
from src.personas import SPEAKER_PERSONAS, TONE_MODIFIERS, get_persona, get_tone_modifier
from src.config import Config

def build_script_prompt(topic: str, tone: str, audience: str, wikipedia_content: str) -> str:
    """
    Build dynamic prompt for Gemini based on topic, tone, and audience
    
    Args:
        topic: Wikipedia topic
        tone: Conversation tone (funny, witty, professional, educational, casual)
        audience: Target audience (kids, teenagers, adults, elders)
        wikipedia_content: Extracted Wikipedia content
        
    Returns:
        Formatted prompt string for LLM
    """
    
    # Get personas
    male_persona = get_persona(audience, "male")
    female_persona = get_persona(audience, "female")
    
    # Get tone modifier
    tone_modifier = get_tone_modifier(tone, audience)
    
    # Build the prompt
    prompt = f"""You are a creative script writer for Indian radio. Generate a natural, conversational 2-minute radio dialogue between two {audience} discussing: **{topic}**

SPEAKER PERSONAS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 {male_persona['name']} ({male_persona['age_range']} years)
   Voice: {male_persona['voice_characteristics']}
   Style: {male_persona['speech_pattern']}
   Vocab: {male_persona['vocabulary']}

👤 {female_persona['name']} ({female_persona['age_range']} years)
   Voice: {female_persona['voice_characteristics']}
   Style: {female_persona['speech_pattern']}
   Vocab: {female_persona['vocabulary']}

TONE: {tone.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{tone_modifier}

HINGLISH LANGUAGE RULES (CRITICAL):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. **Natural Code-Mixing**: Mix Hindi and English like real Indians talk:
   - Hindi for: Emotions (arey, yaar, achha, sahi), reactions, common phrases
   - English for: Technical terms, modern concepts, specific nouns
   - Examples:
     * "Arey yaar, ChatGPT toh bahut advanced AI hai!"
     * "Sachi? Matlab it can write code bhi?"
     * "Haan bro, literally everything kar sakta hai!"

2. **Conversational Elements** (MUST INCLUDE for natural feel):
   - Laughter: [laughs], [giggles], [chuckles]
   - Fillers: [umm], [uh], [hmm]
   - Emotions: [excited], [curious], [surprised], [thoughtful]
   - Pauses: [pause], [sighs]
   - Interruptions: "wait wait...", "suno toh...", "ek minute..."
   - Reactions: "arre wah!", "sachi?", "no way!", "haww!", "kya baat hai!"

3. **Speech Patterns**:
   - Use fillers naturally: "matlab", "basically", "you know", "achha", "toh"
   - Add personality: Agreement ("haan haan", "exactly"), disagreement ("nahi yaar", "but...")
   - Include thinking sounds: "umm", "let me think", "dekhlo"

CONTENT GUIDELINES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use this Wikipedia information (but make it conversational, NOT a lecture):

{wikipedia_content[:1500]}  

Age-Appropriate Content:
- Kids: Relate to school, games, cartoons, simple facts, "did you know?"
- Teenagers: Pop culture, social media, trends, memes, aspirations, relatable scenarios
- Adults: Career implications, real-world applications, economic/social context
- Elders: Historical context, cultural significance, life lessons, traditional values

STRUCTURE REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Total exchanges: 6-8 back-and-forth dialogues
- Each dialogue: 2-4 sentences (25-40 words)
- Total word count: {Config.TARGET_WORD_COUNT_MIN}-{Config.TARGET_WORD_COUNT_MAX} words
- Duration target: ~2 minutes when spoken
- Flow: Introduction → Main discussion → Fun facts/insights → Closing thought

AUTHENTICITY CHECKLIST:
✓ Does it sound like TWO REAL {audience} chatting?
✓ Is the Hinglish natural (not forced translation)?
✓ Are there emotional tags and conversational elements?
✓ Does it match the {tone} tone?
✓ Would this be engaging to listen to?

OUTPUT FORMAT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{male_persona['name']}: [First dialogue with emotion tags]
{female_persona['name']}: [Response with emotion tags]
{male_persona['name']}: [Next dialogue]
{female_persona['name']}: [Response]
... (continue for 6-8 exchanges)

START WRITING NOW! Make it sound AUTHENTIC and {tone}!
"""
    
    return prompt

def validate_generated_script(script: str, audience: str) -> tuple[bool, list]:
    """
    Validate generated script for quality
    
    Returns:
        (is_valid, list_of_issues)
    """
    issues = []
    
    # Check if script has both speakers
    male_persona = get_persona(audience, "male")
    female_persona = get_persona(audience, "female")
    
    if male_persona['name'] not in script:
        issues.append(f"Missing {male_persona['name']} dialogues")
    
    if female_persona['name'] not in script:
        issues.append(f"Missing {female_persona['name']} dialogues")
    
    # Check for conversational elements
    conversational_markers = ['[laughs]', '[giggles]', '[umm]', '[excited]', '[curious]', '[pause]']
    has_markers = any(marker in script for marker in conversational_markers)
    
    if not has_markers:
        issues.append("Script lacks conversational emotion tags")
    
    # Check word count
    word_count = len(script.split())
    if word_count < Config.TARGET_WORD_COUNT_MIN:
        issues.append(f"Script too short ({word_count} words, need {Config.TARGET_WORD_COUNT_MIN}+)")
    elif word_count > Config.TARGET_WORD_COUNT_MAX + 100:
        issues.append(f"Script too long ({word_count} words, max {Config.TARGET_WORD_COUNT_MAX})")
    
    # Check for Hinglish (basic check)
    hindi_words = ['yaar', 'arey', 'achha', 'matlab', 'haan', 'nahi', 'toh', 'hai', 'ka', 'ki']
    has_hindi = any(word in script.lower() for word in hindi_words)
    
    if not has_hindi:
        issues.append("Script might not be in Hinglish (no common Hindi words detected)")
    
    is_valid = len(issues) == 0
    
    return is_valid, issues
