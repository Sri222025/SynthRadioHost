"""
Synth Radio Host - AI Podcast Generator
Generates 2-person Hinglish conversation from Wikipedia
"""

import streamlit as st
import os
import sys
import asyncio
import traceback
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config MUST be first
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
try:
    from src.wikipedia_handler import WikipediaHandler
    WIKI_OK = True
except Exception as e:
    WIKI_OK = False
    wiki_error = str(e)

try:
    from src.script_generator import GroqScriptGenerator
    SCRIPT_OK = True
except Exception as e:
    SCRIPT_OK = False
    script_error = str(e)

try:
    import edge_tts
    TTS_OK = True
except Exception as e:
    TTS_OK = False
    tts_error = str(e)

# Helper Functions
def check_groq_key() -> Optional[str]:
    """Check for Groq API key"""
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")

def get_indian_voices(audience: str) -> tuple:
    """Get Indian English voices for audience"""
    voice_map = {
        "Kids": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Teenagers": ("en-IN-PrabhatNeural", "en-IN-AaravNeural"),
        "Adults": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Elderly": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")
    }
    return voice_map.get(audience, ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"))

async def generate_audio_segment(text: str, voice: str) -> bytes:
    """Generate audio for one dialogue turn"""
    communicate = edge_tts.Communicate(text, voice)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes

def generate_podcast_audio(dialogue: List[Dict], audience: str) -> str:
    """Generate combined audio from dialogue"""
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        voice_male, voice_female = get_indian_voices(audience)
        
        audio_segments = []
        for turn in dialogue:
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            audio_bytes = asyncio.run(generate_audio_segment(text, voice))
            audio_segments.append(audio_bytes)
        
        combined_audio = b"".join(audio_segments)
        
        output_path = output_dir / "podcast.mp3"
        with open(output_path, "wb") as f:
            f.write(combined_audio)
        
        return str(output_path)
    
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        return None

# Initialize Session State
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
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# === HEADER ===
st.title("🎙️ Synth Radio Host")
st.caption("AI-Powered Podcast Generator | Wikipedia se Hinglish Radio tak")

# === SIDEBAR ===
with st.sidebar:
    st.header("🔧 System Status")
    
    groq_key = check_groq_key()
    
    st.success("✅ API Key" if groq_key else "❌ API Key Missing")
    st.success("✅ Wikipedia" if WIKI_OK else f"❌ Wiki: {wiki_error if not WIKI_OK else ''}")
    st.success("✅ Script Gen" if SCRIPT_OK else f"❌ Script: {script_error if not SCRIPT_OK else ''}")
    st.success("✅ TTS Engine" if TTS_OK else f"❌ TTS: {tts_error if not TTS_OK else ''}")
    
    st.divider()
    
    # Configuration (visible after topic selection)
    if st.session_state.selected_topic:
        st.subheader("⚙️ Configure Podcast")
        
        audience = st.selectbox(
            "🎯 Target Audience",
            ["Kids", "Teenagers", "Adults", "Elderly"],
            index=2
        )
        
        duration = st.slider(
            "⏱️ Duration (minutes)",
            min_value=1,
            max_value=5,
            value=2
        )
        
        style = st.selectbox(
            "🎨 Tone",
            ["Informative", "Conversational", "Educational"],
            index=1
        )
        
        st.session_state.config = {
            "audience": audience,
            "duration": duration,
            "style": style
        }

# === MAIN CONTENT ===

# STEP 1: Wikipedia Search
st.subheader("📚 STEP 1: खोजें Wikipedia पे")

col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input(
        "Enter topic keyword (e.g., 'ISRO', 'Cricket', 'AI')",
        placeholder="Type your topic here...",
        key="search_input"
    )

with col2:
    st.write("")
    st.write("")
    search_button = st.button("🔍 Search", use_container_width=True)

# Handle search
if search_button and search_query:
    if not WIKI_OK:
        st.error("❌ Wikipedia handler not available!")
    else:
        with st.spinner("🔍 Searching Wikipedia..."):
            try:
                wiki = WikipediaHandler()
                results = wiki.search_topics(search_query, limit=5)
                
                if results:
                    st.session_state.search_results = results
                    st.session_state.current_step = 2
                    st.success(f"✅ Found {len(results)} topics!")
                else:
                    st.warning("⚠️ No topics found. Try a different keyword.")
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")

# STEP 2: Select Topic
if st.session_state.search_results:
    st.divider()
    st.subheader("📝 STEP 2: चुनिए Topic")
    
    for idx, result in enumerate(st.session_state.search_results):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {result.get('title', 'Unknown')}")
                st.write(result.get('description', 'No description available'))
            
            with col2:
                st.write("")
                if st.button("✔️ Select", key=f"select_{idx}", use_container_width=True):
                    with st.spinner("📄 Fetching article..."):
                        try:
                            wiki = WikipediaHandler()
                            content = wiki.get_article_content(
                                result['title'],
                                max_chars=5000
                            )
                            
                            if content:
                                st.session_state.selected_topic = result['title']
                                st.session_state.wiki_content = content
                                st.session_state.current_step = 3
                                st.success(f"✅ Selected: {result['title']}")
                                st.rerun()
                            else:
                                st.error("❌ Could not fetch article content")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        st.divider()

# STEP 3: Generate Script
if st.session_state.selected_topic and st.session_state.wiki_content:
    st.divider()
    st.subheader("🎬 STEP 3: Generate Script")
    
    st.info(f"**📌 Selected Topic:** {st.session_state.selected_topic}")
    
    config = st.session_state.get('config', {
        "audience": "Adults",
        "duration": 2,
        "style": "Conversational"
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            if not SCRIPT_OK:
                st.error("❌ Script generator not available!")
            elif not groq_key:
                st.error("❌ GROQ_API_KEY not found in secrets!")
            else:
                with st.spinner("✨ Generating Hinglish conversation..."):
                    try:
                        generator = GroqScriptGenerator(api_key=groq_key)
                        
                        result = generator.generate_script(
                            topic=st.session_state.selected_topic,
                            wikipedia_content=st.session_state.wiki_content[:3000],
                            duration_minutes=config["duration"],
                            style=config["style"],
                            audience=config["audience"]
                        )
                        
                        if result.get("success"):
                            st.session_state.script_data = result
                            st.session_state.current_step = 4
                            st.success("✅ Script generated!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.session_state.script_data:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.script_data = None
                st.session_state.audio_path = None
                st.rerun()

# STEP 4: Display Script
if st.session_state.script_data:
    st.divider()
    st.subheader("📄 Generated Script")
    
    data = st.session_state.script_data
    
    # Title
    if "title" in data:
        st.markdown(f"### 🎙️ {data['title']}")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Speakers", "2 (Rajesh & Priya)")
    with col2:
        st.metric("⏱️ Duration", f"~{config.get('duration', 2)} min")
    with col3:
        st.metric("🎯 Audience", config.get('audience', 'Adults'))
    
    # Dialogue
    if "dialogue" in data:
        st.markdown("#### 💬 Conversation:")
        
        for turn in data["dialogue"]:
            speaker = turn.get("speaker", "Unknown")
            text = turn.get("text", "")
            
            if speaker == "Rajesh":
                st.markdown(f"**🙋‍♂️ {speaker}:** {text}")
            else:
                st.markdown(f"**🙋‍♀️ {speaker}:** {text}")

# STEP 5: Generate Audio
if st.session_state.script_data:
    st.divider()
    st.subheader("🎵 STEP 4: Generate Audio")
    
    if not st.session_state.audio_path:
        if st.button("🎤 Generate Podcast Audio", type="primary", use_container_width=True):
            if not TTS_OK:
                st.error("❌ TTS engine not available!")
            else:
                with st.spinner("🎙️ Generating audio... (1-2 minutes)"):
                    try:
                        dialogue = st.session_state.script_data.get("dialogue", [])
                        audience = config.get("audience", "Adults")
                        
                        audio_path = generate_podcast_audio(dialogue, audience)
                        
                        if audio_path:
                            st.session_state.audio_path = audio_path
                            st.session_state.current_step = 5
                            st.success("✅ Audio ready!")
                            st.rerun()
                        else:
                            st.error("❌ Audio generation failed")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    else:
        # Display audio
        if Path(st.session_state.audio_path).exists():
            st.success("✅ Your podcast is ready!")
            
            with open(st.session_state.audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                file_size = len(audio_bytes) / (1024 * 1024)
                voice_male, voice_female = get_indian_voices(config.get("audience", "Adults"))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 File Size: {file_size:.2f} MB")
                with col2:
                    st.info(f"🎙️ Voices: Indian English")
                
                st.download_button(
                    label="⬇️ Download Podcast (MP3)",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}_podcast.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                if st.button("🔄 Generate New Audio", use_container_width=True):
                    st.session_state.audio_path = None
                    st.rerun()
        else:
            st.error("❌ Audio file not found!")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Groq AI, and Microsoft Edge TTS")
