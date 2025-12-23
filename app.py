"""
Synth Radio Host - Wikipedia to Podcast Generator
Hackathon Version with Audience Adaptation
Single-file version with embedded Groq support + Edge TTS
"""

import streamlit as st
import os
import sys
import json
import re
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from groq import Groq
import edge_tts

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Wikipedia handler
try:
    from src.wikipedia_handler import WikipediaHandler
    WIKI_OK = True
except Exception as e:
    WIKI_OK = False
    wiki_error = str(e)


# ============================================
# EMBEDDED GROQ SCRIPT GENERATOR
# ============================================

class EmbeddedGroqScriptGenerator:
    """Embedded Groq-based script generator"""
    
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
    
    def __init__(self, api_key: str):
        """Initialize Groq client"""
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def _build_prompt(self, wikipedia_content: str, topic_title: str, 
                     duration_minutes: int, style: str, audience: str) -> str:
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
    
    def generate_script(self, wikipedia_content: str, topic_title: str,
                       duration_minutes: int = 3, style: str = "Educational",
                       audience: str = "Adults (19-60)") -> Dict[str, Any]:
        """Generate podcast script using Groq"""
        
        try:
            if not wikipedia_content or not wikipedia_content.strip():
                return {"success": False, "error": "Wikipedia content is empty"}
            
            if not 1 <= duration_minutes <= 10:
                return {"success": False, "error": "Duration must be between 1 and 10 minutes"}
            
            # Build prompt
            prompt = self._build_prompt(wikipedia_content, topic_title, 
                                       duration_minutes, style, audience)
            
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
                return {"success": False, "error": "No response from Groq API"}
            
            # Parse JSON
            script_data = self._extract_json(response_text)
            
            if not script_data:
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


# ============================================
# EDGE TTS VOICE SELECTOR
# ============================================

def get_voice_for_audience(audience: str) -> str:
    """Select appropriate Edge TTS voice based on audience"""
    voice_map = {
        "Kids (5-12)": "en-US-JennyNeural",      # Friendly, warm female
        "Teenagers (13-18)": "en-US-AriaNeural",  # Young, energetic female
        "Adults (19-60)": "en-US-AndrewNeural",   # Professional male
        "Elderly (60+)": "en-US-GuyNeural"        # Warm, mature male
    }
    return voice_map.get(audience, "en-US-AndrewNeural")


# ============================================
# HELPER FUNCTIONS
# ============================================

def check_groq_key():
    """Check for Groq API key"""
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")


# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None
if 'wiki_content' not in st.session_state:
    st.session_state.wiki_content = None
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None


# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    .topic-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .topic-card:hover {
        border-color: #FF6B6B;
        box-shadow: 0 2px 8px rgba(255,107,107,0.2);
    }
    .groq-badge {
        background-color: #f4a261;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .tts-badge {
        background-color: #2a9d8f;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# HEADER
# ============================================

st.title("🎙️ Synth Radio Host")
st.caption("Wikipedia to Podcast - AI-Powered with Audience Adaptation")


# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.header("🔧 System Status")
    
    groq_key = check_groq_key()
    
    if groq_key:
        st.success("✅ Groq API (Llama 3.3 70B)")
    else:
        st.error("❌ Groq API Key Missing")
        st.info("💡 Add GROQ_API_KEY to Streamlit Secrets")
    
    if WIKI_OK:
        st.success("✅ Wikipedia API")
    else:
        st.error(f"❌ Wikipedia: {wiki_error}")
    
    st.success("✅ Edge TTS (Microsoft)")
    
    st.divider()
    
    st.header("📍 Progress")
    steps = ["🔍 Search", "✅ Select", "⚙️ Configure", "🎵 Generate"]
    for i, step_name in enumerate(steps, 1):
        if i < st.session_state.step:
            st.success(f"{step_name} ✓")
        elif i == st.session_state.step:
            st.info(f"**→ {step_name}**")
        else:
            st.text(step_name)
    
    st.divider()
    
    with st.expander("ℹ️ About the Tech"):
        st.markdown("""
        **Groq AI**
        - 🚀 Lightning fast (2-5 seconds)
        - 🆓 14,400 requests/day FREE
        - 🧠 Llama 3.3 70B model
        
        **Microsoft Edge TTS**
        - 🎙️ Natural-sounding voices
        - 🆓 Unlimited & free
        - 🎯 Audience-matched voices
        
        **Get Groq API Key:**
        Visit: console.groq.com
        """)


# ============================================
# STEP 1: SEARCH WIKIPEDIA
# ============================================

if st.session_state.step == 1:
    st.header("🔍 Step 1: Search Wikipedia Topics")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_keyword = st.text_input(
            "Enter search keyword",
            placeholder="e.g., Artificial Intelligence, Climate Change, Black Holes",
            key="search_input"
        )
    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("🔎 Search", type="primary", use_container_width=True)
    
    if search_btn:
        if not search_keyword.strip():
            st.error("❌ Please enter a search keyword!")
        elif not WIKI_OK:
            st.error("❌ Wikipedia handler not available!")
        else:
            with st.spinner("🔍 Searching Wikipedia..."):
                wiki = WikipediaHandler()
                results = wiki.search_topics(search_keyword, limit=10)
                
                if results:
                    st.session_state.search_results = results
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("❌ No topics found. Try a different keyword.")


# ============================================
# STEP 2: SELECT TOPIC
# ============================================

elif st.session_state.step == 2:
    st.header("✅ Step 2: Select a Topic")
    
    st.info(f"📚 Found {len(st.session_state.search_results)} topics related to your search")
    
    for idx, result in enumerate(st.session_state.search_results):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.subheader(result['title'])
                st.caption(result['snippet'])
                if result.get('description'):
                    st.write(f"*{result['description']}*")
            
            with col2:
                st.write("")
                if st.button("Select →", key=f"select_{idx}", use_container_width=True):
                    with st.spinner(f"📖 Fetching '{result['title']}'..."):
                        wiki = WikipediaHandler()
                        content = wiki.get_article_content(result['title'], max_chars=3000)
                        
                        st.session_state.selected_topic = result['title']
                        st.session_state.wiki_content = content
                        st.session_state.step = 3
                        st.rerun()
            
            st.divider()
    
    if st.button("← Back to Search"):
        st.session_state.step = 1
        st.rerun()


# ============================================
# STEP 3: CONFIGURE & GENERATE
# ============================================

elif st.session_state.step == 3:
    st.header("⚙️ Step 3: Configure Your Podcast")
    
    st.success(f"📚 Selected Topic: **{st.session_state.selected_topic}**")
    
    with st.expander("📖 View Wikipedia Summary"):
        st.write(st.session_state.wiki_content['summary'])
        st.caption(f"[Read full article]({st.session_state.wiki_content['url']})")
    
    st.divider()
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Target Audience")
        audience = st.radio(
            "Who is this podcast for?",
            options=["Kids (5-12)", "Teenagers (13-18)", "Adults (19-60)", "Elderly (60+)"],
            index=2,
            key="audience_select",
            help="Different vocabulary, tone, and voice will be used for each audience"
        )
        
        # Show which voice will be used
        voice = get_voice_for_audience(audience)
        voice_names = {
            "en-US-JennyNeural": "Jenny (Warm & Friendly)",
            "en-US-AriaNeural": "Aria (Young & Energetic)",
            "en-US-AndrewNeural": "Andrew (Professional)",
            "en-US-GuyNeural": "Guy (Warm & Mature)"
        }
        st.info(f"**🎯 USP**: Content adapted for {audience}\n\n🎙️ **Voice**: {voice_names.get(voice, voice)}")
    
    with col2:
        st.subheader("🎨 Style & Duration")
        
        style = st.selectbox(
            "Presentation Style",
            options=["Educational", "Informative", "Conversational", "Entertaining", "Story-telling"],
            key="style_select"
        )
        
        duration = st.slider(
            "Duration (minutes)",
            min_value=1,
            max_value=10,
            value=3,
            key="duration_slider"
        )
    
    st.divider()
    
    # API check
    groq_key = check_groq_key()
    
    if groq_key:
        st.success("🚀 Ready to generate with **Groq (Llama 3.3 70B)** + **Microsoft Edge TTS**")
    else:
        st.error("❌ GROQ_API_KEY not configured! Please add it to Streamlit Secrets.")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Podcast Script", type="primary", use_container_width=True, disabled=not groq_key)
    
    if generate_btn and groq_key:
        with st.spinner(f"🤖 Generating {duration}-min {style} podcast for {audience}..."):
            try:
                generator = EmbeddedGroqScriptGenerator(api_key=groq_key)
                
                result = generator.generate_script(
                    wikipedia_content=st.session_state.wiki_content['full_text'],
                    topic_title=st.session_state.selected_topic,
                    duration_minutes=duration,
                    style=style,
                    audience=audience
                )
                
                if result.get("success"):
                    st.session_state.script_data = result
                    st.session_state.audio_path = None
                    st.session_state.step = 4
                    st.success("✅ Script generated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ Generation failed: {result.get('error')}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())
    
    if st.button("← Change Topic"):
        st.session_state.step = 2
        st.rerun()


# ============================================
# STEP 4: SCRIPT GENERATED
# ============================================

elif st.session_state.step == 4:
    st.header("📄 Generated Podcast Script")
    
    script_data = st.session_state.script_data
    
    # Metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Topic", st.session_state.selected_topic[:20] + "..." if len(st.session_state.selected_topic) > 20 else st.session_state.selected_topic)
    with col2:
        audience_short = script_data.get('target_audience', 'N/A').split('(')[0].strip()
        st.metric("Audience", audience_short)
    with col3:
        st.metric("Duration", f"{script_data.get('total_duration', 0)//60} min")
    with col4:
        st.markdown('<span class="groq-badge">Groq AI</span><span class="tts-badge">Edge TTS</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Script display
    col_script, col_audio = st.columns([2, 1])
    
    with col_script:
        st.subheader(f"📻 {script_data.get('title', 'Podcast Script')}")
        
        if script_data.get('description'):
            st.info(script_data['description'])
        
        # Key adaptations
        if script_data.get('key_adaptations'):
            with st.expander("🎯 Audience Adaptations (Our USP!)"):
                st.markdown("**How we adapted this content:**")
                for adaptation in script_data['key_adaptations']:
                    st.write(f"✓ {adaptation}")
        
        # Full script
        st.text_area(
            "Full Script",
            value=script_data.get("script", ""),
            height=400,
            key="script_display"
        )
        
        # Segments
        if script_data.get('segments'):
            st.markdown("#### 📋 Script Breakdown")
            for i, seg in enumerate(script_data['segments'], 1):
                with st.expander(f"Segment {i}: {seg.get('type', 'main').title()} ({seg.get('duration')}s)"):
                    st.write(seg.get('text', ''))
                    if seg.get('notes'):
                        st.caption(f"💡 {seg['notes']}")
        
        st.divider()
        if st.button("🔄 Regenerate Script", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    
    with col_audio:
        st.subheader("🎵 Audio Generation")
        
        if st.session_state.audio_path:
            st.success("✅ Audio Ready!")
            
            audio_file = Path(st.session_state.audio_path)
            if audio_file.exists():
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                
                st.audio(audio_bytes, format="audio/mp3")
                
                # Show file info
                file_size_kb = len(audio_bytes) / 1024
                st.caption(f"📊 Size: {file_size_kb:.1f} KB")
                
                # Show voice used
                audience = script_data.get('target_audience', 'Adults (19-60)')
                voice = get_voice_for_audience(audience)
                voice_names = {
                    "en-US-JennyNeural": "Jenny",
                    "en-US-AriaNeural": "Aria",
                    "en-US-AndrewNeural": "Andrew",
                    "en-US-GuyNeural": "Guy"
                }
                st.caption(f"🎙️ Voice: {voice_names.get(voice, voice)}")
                
                st.download_button(
                    label="⬇️ Download Podcast",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
        else:
            st.info("Click below to generate audio from the script")
            
            # Show which voice will be used
            audience = script_data.get('target_audience', 'Adults (19-60)')
            voice = get_voice_for_audience(audience)
            voice_names = {
                "en-US-JennyNeural": "Jenny (Warm & Friendly)",
                "en-US-AriaNeural": "Aria (Young & Energetic)",
                "en-US-AndrewNeural": "Andrew (Professional)",
                "en-US-GuyNeural": "Guy (Warm & Mature)"
            }
            st.caption(f"🎙️ Will use: {voice_names.get(voice, voice)}")
            
            if st.button("🎤 Generate Audio", type="primary", use_container_width=True):
                try:
                    with st.spinner("🎵 Generating audio with Microsoft Edge TTS..."):
                        Path("outputs").mkdir(exist_ok=True)
                        
                        # Combine all segments
                        segments = script_data.get('segments', [])
                        full_text = "\n\n".join([s.get('text', '') for s in segments])
                        
                        safe_filename = st.session_state.selected_topic.replace(' ', '_').replace('/', '-')
                        audio_path = f"outputs/{safe_filename}.mp3"
                        
                        # Get audience-appropriate voice
                        voice = get_voice_for_audience(audience)
                        
                        # Generate audio with Edge TTS
                        async def generate_audio():
                            communicate = edge_tts.Communicate(full_text, voice)
                            await communicate.save(audio_path)
                        
                        # Run async function
                        asyncio.run(generate_audio())
                        
                        st.session_state.audio_path = audio_path
                        st.success("✅ Audio generated!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Audio generation failed: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
        
        st.divider()
        
        if st.button("← New Topic", use_container_width=True):
            st.session_state.step = 1
            st.session_state.search_results = []
            st.session_state.selected_topic = None
            st.session_state.script_data = None
            st.session_state.audio_path = None
            st.rerun()


# ============================================
# FOOTER
# ============================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🏆 <strong>Hackathon Project</strong></p>
    <p style="font-size: 0.9rem;">Built with ❤️ using Streamlit, Wikipedia API, Groq AI & Microsoft Edge TTS</p>
    <p style="font-size: 0.85rem;"><strong>USP:</strong> Audience-adapted scripts with matching voices for each demographic</p>
</div>
""", unsafe_allow_html=True)
