"""
Speaker persona definitions for different audiences
"""

SPEAKER_PERSONAS = {
    "kids": {
        "male": {
            "name": "BOY",
            "display_name": "Boy (8-12 years)",
            "age_range": "8-12",
            "voice_characteristics": "High-pitched, energetic, enthusiastic",
            "speech_pattern": "Short sentences, lots of questions, exclamations",
            "vocabulary": "Simple words, avoid jargon, use kid-friendly analogies",
            "bark_voice": "v2/en_speaker_6",
            "elevenlabs_voice": "adam",  # Will map to appropriate voice
            "hinglish_ratio": 0.3,  # 30% Hindi, 70% English
        },
        "female": {
            "name": "GIRL",
            "display_name": "Girl (8-12 years)",
            "age_range": "8-12",
            "voice_characteristics": "Cheerful, curious, expressive",
            "speech_pattern": "Excited reactions, wonder expressions, giggles",
            "vocabulary": "Simple, relatable to school/play experiences",
            "bark_voice": "v2/en_speaker_9",
            "elevenlabs_voice": "bella",
            "hinglish_ratio": 0.3,
        }
    },
    
    "teenagers": {
        "male": {
            "name": "TEEN BOY",
            "display_name": "Teen Boy (13-19 years)",
            "age_range": "13-19",
            "voice_characteristics": "Casual, confident, slightly deeper",
            "speech_pattern": "Slang, 'bro', 'yaar', pop culture references",
            "vocabulary": "Mix of Hindi-English slang, trendy terms",
            "bark_voice": "v2/en_speaker_7",
            "elevenlabs_voice": "josh",
            "hinglish_ratio": 0.6,  # 60% Hindi/slang mix
        },
        "female": {
            "name": "TEEN GIRL",
            "display_name": "Teen Girl (13-19 years)",
            "age_range": "13-19",
            "voice_characteristics": "Witty, expressive, animated",
            "speech_pattern": "Sarcastic humor, dramatic reactions, 'literally', 'like'",
            "vocabulary": "Teen slang, social media lingo, expressive",
            "bark_voice": "v2/en_speaker_1",
            "elevenlabs_voice": "elli",
            "hinglish_ratio": 0.6,
        }
    },
    
    "adults": {
        "male": {
            "name": "SPEAKER 1",
            "display_name": "Professional Man (25-45 years)",
            "age_range": "25-45",
            "voice_characteristics": "Clear, authoritative, professional",
            "speech_pattern": "Balanced pace, thoughtful pauses, articulate",
            "vocabulary": "Professional, nuanced, contextually rich",
            "bark_voice": "v2/en_speaker_3",
            "elevenlabs_voice": "adam",
            "hinglish_ratio": 0.4,
        },
        "female": {
            "name": "SPEAKER 2",
            "display_name": "Professional Woman (25-45 years)",
            "age_range": "25-45",
            "voice_characteristics": "Polished, articulate, warm professional",
            "speech_pattern": "Measured delivery, analytical, engaging",
            "vocabulary": "Sophisticated, precise, professionally conversational",
            "bark_voice": "v2/en_speaker_2",
            "elevenlabs_voice": "aria",
            "hinglish_ratio": 0.4,
        }
    },
    
    "elders": {
        "male": {
            "name": "ELDER",
            "display_name": "Senior Man (50+ years)",
            "age_range": "50+",
            "voice_characteristics": "Warm, wise, patient, deeper tone",
            "speech_pattern": "Slower pace, clear pronunciation, life wisdom",
            "vocabulary": "Traditional references, cultural context, respectful",
            "bark_voice": "v2/en_speaker_4",
            "elevenlabs_voice": "sam",
            "hinglish_ratio": 0.7,  # More Hindi
        },
        "female": {
            "name": "ELDER",
            "display_name": "Senior Woman (50+ years)",
            "age_range": "50+",
            "voice_characteristics": "Gentle, respectful, nurturing, softer",
            "speech_pattern": "Patient delivery, storytelling style, calm",
            "vocabulary": "Cultural values, traditional wisdom, respectful Hindi",
            "bark_voice": "v2/en_speaker_8",
            "elevenlabs_voice": "rachel",
            "hinglish_ratio": 0.7,
        }
    }
}

TONE_MODIFIERS = {
    "funny": {
        "kids": "Make silly jokes, use fun sound effects [giggles], compare to cartoons and games. Keep it light and playful!",
        "teenagers": "Use sarcastic humor, meme references, witty comebacks, and roasting style. Make it savage but fun!",
        "adults": "Clever wordplay, situational humor, irony, and subtle jokes. Keep it sophisticated.",
        "elders": "Light-hearted anecdotes, gentle humor from life experiences. Keep it warm and relatable."
    },
    
    "witty": {
        "kids": "Smart observations, 'aha!' moments, clever questions that make them think.",
        "teenagers": "Quick comebacks, pop culture burns, sarcastic comments, and 'savage' remarks.",
        "adults": "Intellectual humor, wordplay, sharp observations, and dry wit.",
        "elders": "Wise quips, proverbs with a twist, and subtle cleverness."
    },
    
    "professional": {
        "kids": "Like a cool teacher explaining things clearly and simply.",
        "teenagers": "Like a mentor or coach - direct but relatable.",
        "adults": "Colleague-to-colleague informed discussion with analytical depth.",
        "elders": "Respectful expertise with seasoned perspective and balance."
    },
    
    "educational": {
        "kids": "Step-by-step like story time, with lots of 'why?' and 'how?' questions.",
        "teenagers": "Engaging lecture style with real-world examples and career relevance.",
        "adults": "In-depth analysis with nuanced perspectives and practical implications.",
        "elders": "Contextual history, connecting to past experiences, and wisdom sharing."
    },
    
    "casual": {
        "kids": "Like chatting with a friend during recess - fun and easy!",
        "teenagers": "Chill conversation like hanging out with friends - relaxed vibes.",
        "adults": "Friendly professional chat - like coffee break discussions.",
        "elders": "Warm conversation like family gathering - comfortable and respectful."
    }
}

def get_persona(audience: str, gender: str) -> dict:
    """Get speaker persona for given audience and gender"""
    return SPEAKER_PERSONAS.get(audience, {}).get(gender, {})

def get_tone_modifier(tone: str, audience: str) -> str:
    """Get tone modifier for given tone and audience"""
    return TONE_MODIFIERS.get(tone, {}).get(audience, "")
