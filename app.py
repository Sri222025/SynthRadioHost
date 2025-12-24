"""
Synth Radio Host - AI Podcast Generator
Generates 2-person Hinglish conversation from Wikipedia
Mobile-First Design with Jio Theme
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

# Jio-inspired Mobile-First CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    :root {
        --jio-blue: #0a2885;
        --jio-light-blue: #2563eb;
        --jio-bg: #f8fafc;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    
    @media (min-width: 768px) {
        .main .block-container {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
    }
    
    h1 {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
    }
    
    @media (min-width: 768px) {
        h1 {
            font-size: 2.5rem !important;
        }
    }
    
    h2 {
        color: var(--jio-blue) !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--jio-blue) 0%, var(--jio-light-blue) 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(10, 40, 133, 0.2) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(10, 40, 133, 0.4) !important;
    }
    
    .topic-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--jio-blue) !important;
    }
</style>
""", unsafe_allow_html=True)

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
if 'num_results' not in st.session_state:
    st.session_state.num_results = 10

# === HEADER ===
st.title("🎙️ Synth Radio Host")
st.caption("AI-Powered Podcast Generator | Wikipedia se Hinglish Radio tak")
st.divider()

# === SIDEBAR ===
with st.sidebar:
    st.header("🔧 System Status")
    
    groq_key = check_groq_key()
    
    st.success("✅ API Key" if groq_key else "❌ API Key Missing")
    st.success("✅ Wikipedia" if WIKI_OK else "❌ Wikipedia")
    st.success("✅ AI Script" if SCRIPT_OK else "❌ AI Script")
    st.success("✅ TTS Engine" if TTS_OK else "❌ TTS Engine")
    
    st.divider()
    
    st.subheader("⚙️ Search Settings")
    st.session_state.num_results = st.slider(
        "Number of results",
        min_value=5,
        max_value=20,
        value=10,
        step=5
    )
    
    st.divider()
    
    if st.session_state.selected_topic:
        st.subheader("🎯 Podcast Config")
        
        audience = st.selectbox(
            "Target Audience",
            ["Kids", "Teenagers", "Adults", "Elderly"],
            index=2
        )
        
        duration = st.slider(
            "Duration (minutes)",
            min_value=1,
            max_value=5,
            value=2
        )
        
        style = st.selectbox(
            "Tone",
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

search_query = st.text_input(
    "Enter topic keyword",
    placeholder="e.g., ISRO, Cricket, AI...",
    key="search_input"
)

search_button = st.button("🔍 Search Wikipedia", use_container_width=True, type="primary")

if search_button and search_query:
    if not WIKI_OK:
        st.error("❌ Wikipedia handler not available!")
    else:
        with st.spinner("🔍 Searching..."):
            try:
                wiki = WikipediaHandler()
                results = wiki.search_topics(search_query, limit=st.session_state.num_results)
                
                if results:
                    st.session_state.search_results = results
                    st.success(f"✅ Found {len(results)} topics!")
                else:
                    st.warning("⚠️ No topics found.")
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")

# STEP 2: Select Topic
if st.session_state.search_results:
    st.divider()
    st.subheader(f"📝 STEP 2: Select Topic ({len(st.session_state.search_results)} results)")
    
    for idx, result in enumerate(st.session_state.search_results):
        with st.container():
            st.markdown(f"""
            <div class="topic-card">
                <h3>📄 {result.get('title', 'Unknown')}</h3>
                <p style="color: #64748b;">{result.get('description', '')[:200]}...</p>
            </div>
            """, unsafe_allow_html=True)
            
            select_key = f"select_{idx}_{result.get('title', idx)}"
            if st.button("✔️ Select", key=select_key, use_container_width=True):
                with st.spinner("📄 Fetching..."):
                    try:
                        wiki = WikipediaHandler()
                        content = wiki.get_article_content(result['title'], max_chars=5000)
                        
                        if content:
                            st.session_state.selected_topic = result['title']
                            st.session_state.wiki_content = content
                            st.session_state.search_results = []
                            st.success(f"✅ Selected: {result['title']}")
                            st.rerun()
                        else:
                            st.error("❌ Could not fetch content")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# STEP 3: Generate Script
if st.session_state.selected_topic and st.session_state.wiki_content:
    st.divider()
    st.subheader("🎬 STEP 3: Generate Script")
    
    st.info(f"**📌 Topic:** {st.session_state.selected_topic}")
    
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
                st.error("❌ GROQ_API_KEY not found!")
            else:
                with st.spinner("✨ Generating... (30-60s)"):
                    try:
                        generator = GroqScriptGenerator(api_key=groq_key)
                        
                        # Convert wiki_content to string safely
                        wiki_text = st.session_state.wiki_content
                        
                        if isinstance(wiki_text, dict):
                            wiki_text = (
                                wiki_text.get('content', '') or 
                                wiki_text.get('text', '') or 
                                wiki_text.get('extract', '') or 
                                str(wiki_text)
                            )
                        elif isinstance(wiki_text, list):
                            wiki_text = ' '.join(str(item) for item in wiki_text)
                        elif wiki_text is None:
                            wiki_text = ""
                        else:
                            wiki_text = str(wiki_text)
                        
                        wiki_text = wiki_text[:3000]
                        
                        result = generator.generate_script(
                            topic=st.session_state.selected_topic,
                            wikipedia_content=wiki_text,
                            duration_minutes=config["duration"],
                            style=config["style"],
                            audience=config["audience"]
                        )
                        
                        if result.get("success"):
                            st.session_state.script_data = result
                            st.success("✅ Script generated!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        with st.expander("🔍 Debug"):
                            st.code(traceback.format_exc())
    
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
    
    if "title" in data:
        st.markdown(f"### 🎙️ {data['title']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Speakers", "2")
    with col2:
        st.metric("⏱️ Duration", f"~{config.get('duration', 2)} min")
    with col3:
        st.metric("🎯 Audience", config.get('audience', 'Adults'))
    
    st.divider()
    
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
        if st.button("🎤 Generate Audio", type="primary", use_container_width=True):
            if not TTS_OK:
                st.error("❌ TTS not available!")
            else:
                with st.spinner("🎙️ Generating... (1-2 min)"):
                    try:
                        dialogue = st.session_state.script_data.get("dialogue", [])
                        audience = config.get("audience", "Adults")
                        
                        audio_path = generate_podcast_audio(dialogue, audience)
                        
                        if audio_path:
                            st.session_state.audio_path = audio_path
                            st.success("✅ Audio ready!")
                            st.rerun()
                        else:
                            st.error("❌ Audio failed")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        if Path(st.session_state.audio_path).exists():
            st.success("✅ Podcast ready!")
            
            with open(st.session_state.audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                file_size = len(audio_bytes) / (1024 * 1024)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 Size: {file_size:.2f} MB")
                with col2:
                    st.info("🎙️ Indian Voices")
                
                st.download_button(
                    label="⬇️ Download MP3",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}_podcast.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                if st.button("🔄 New Audio", use_container_width=True):
                    st.session_state.audio_path = None
                    st.rerun()

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Groq AI & Microsoft Edge TTS")
