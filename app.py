"""
Synth Radio Host - AI Podcast Generator
Generates 2-person Hinglish conversation from Wikipedia
No pydub - Works on Python 3.13+
"""

import streamlit as st
import os
import sys
import asyncio
import json
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

# Jio-inspired CSS (FIXED: Progress bar rendering)
st.markdown("""
<style>
    /* Jio Blue Theme */
    :root {
        --jio-blue: #0a2885;
        --jio-light-blue: #2563eb;
        --jio-bg: #f8fafc;
    }
    
    /* Main Layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Headers */
    h1 {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
    }
    
    h2, h3 {
        color: var(--jio-blue) !important;
        font-weight: 600 !important;
    }
    
    /* Cards */
    .stCard {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--jio-blue) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--jio-light-blue) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(10,40,133,0.3);
    }
    
    /* Progress Steps - FIXED */
    .progress-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 0 1rem;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .step-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.25rem;
        z-index: 2;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: var(--jio-blue);
        color: white;
        box-shadow: 0 4px 12px rgba(10,40,133,0.3);
    }
    
    .step-circle.completed {
        background: #10b981;
        color: white;
    }
    
    .step-label {
        margin-top: 0.5rem;
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
    }
    
    .step-label.active {
        color: var(--jio-blue);
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .progress-container {
            flex-direction: column;
            gap: 1rem;
        }
        
        .progress-step {
            flex-direction: row;
            width: 100%;
            justify-content: flex-start;
        }
        
        .step-label {
            margin-top: 0;
            margin-left: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Import modules with error handling
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
        
        # Get voices
        voice_male, voice_female = get_indian_voices(audience)
        
        # Generate all segments
        audio_segments = []
        for turn in dialogue:
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            audio_bytes = asyncio.run(generate_audio_segment(text, voice))
            audio_segments.append(audio_bytes)
        
        # Combine all audio
        combined_audio = b"".join(audio_segments)
        
        # Save to file
        output_path = output_dir / "podcast.mp3"
        with open(output_path, "wb") as f:
            f.write(combined_audio)
        
        return str(output_path)
    
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        return None

def render_progress_steps(current_step: int):
    """Render progress indicator - FIXED"""
    steps = ["खोज", "Select", "Configure", "Script", "Audio"]
    
    html = '<div class="progress-container">'
    
    for i, label in enumerate(steps, 1):
        step_class = "step-circle"
        label_class = "step-label"
        
        if i < current_step:
            step_class += " completed"
        elif i == current_step:
            step_class += " active"
            label_class += " active"
        
        html += f'''
        <div class="progress-step">
            <div class="{step_class}">{i}</div>
            <div class="{label_class}">{label}</div>
        </div>
        '''
    
    html += '</div>'
    
    # CRITICAL FIX: Add unsafe_allow_html=True
    st.markdown(html, unsafe_allow_html=True)

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

# Progress indicator
render_progress_steps(st.session_state.current_step)

st.divider()

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

if search_button and search_query:
    if not WIKI_OK:
        st.error("Wikipedia handler not available!")
    else:
        with st.spinner("Searching Wikipedia..."):
            try:
                wiki = WikipediaHandler()
                results = wiki.search_topics(search_query, limit=5)
                
                if results:
                    st.session_state.search_results = results
                    st.session_state.current_step = 2
                    st.success(f"✅ Found {len(results)} topics!")
                    st.rerun()
                else:
                    st.warning("No topics found. Try a different keyword.")
            except Exception as e:
                st.error(f"Search failed: {str(e)}")

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
                if st.button("Select", key=f"select_{idx}", use_container_width=True):
                    if not WIKI_OK:
                        st.error("Wikipedia handler not available!")
                    else:
                        with st.spinner("Fetching article..."):
                            try:
                                wiki = WikipediaHandler()
                                content = wiki.get_article_content(
                                    result['title'],
                                    max_chars=5000  # FIXED: Changed from sentences=20
                                )
                                
                                if content:
                                    st.session_state.selected_topic = result['title']
                                    st.session_state.wiki_content = content
                                    st.session_state.current_step = 3
                                    st.success(f"✅ Selected: {result['title']}")
                                    st.rerun()
                                else:
                                    st.error("Could not fetch article content")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            st.divider()

# STEP 3: Generate Script
if st.session_state.selected_topic and st.session_state.wiki_content:
    st.divider()
    st.subheader("🎬 STEP 3: Generate Script")
    
    st.info(f"**Selected Topic:** {st.session_state.selected_topic}")
    
    config = st.session_state.get('config', {
        "audience": "Adults",
        "duration": 2,
        "style": "Conversational"
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            if not SCRIPT_OK:
                st.error("Script generator not available!")
            elif not groq_key:
                st.error("GROQ_API_KEY not found in secrets!")
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
                            st.success("✅ Script generated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        with st.expander("🔍 Full Error Details"):
                            st.code(traceback.format_exc())
    
    with col2:
        if st.session_state.script_data:
            if st.button("🔄 Regenerate Script", use_container_width=True):
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
        st.metric("Speakers", "2 (Rajesh & Priya)")
    with col2:
        st.metric("Duration", f"~{config.get('duration', 2)} min")
    with col3:
        st.metric("Audience", config.get('audience', 'Adults'))
    
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
                st.error("TTS engine not available!")
            else:
                with st.spinner("🎙️ Generating audio... This may take 1-2 minutes"):
                    try:
                        dialogue = st.session_state.script_data.get("dialogue", [])
                        audience = config.get("audience", "Adults")
                        
                        audio_path = generate_podcast_audio(dialogue, audience)
                        
                        if audio_path:
                            st.session_state.audio_path = audio_path
                            st.session_state.current_step = 5
                            st.success("✅ Audio generated successfully!")
                            st.rerun()
                        else:
                            st.error("Audio generation failed")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        with st.expander("🔍 Error Details"):
                            st.code(traceback.format_exc())
    
    else:
        # Display audio player
        if Path(st.session_state.audio_path).exists():
            st.success("✅ Your podcast is ready!")
            
            with open(st.session_state.audio_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                # File info
                file_size = len(audio_bytes) / (1024 * 1024)
                voice_male, voice_female = get_indian_voices(config.get("audience", "Adults"))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 File Size: {file_size:.2f} MB")
                with col2:
                    st.info(f"🎙️ Voices: {voice_male.split('-')[1]} & {voice_female.split('-')[1]}")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Podcast (MP3)",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}_podcast.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                # Regenerate option
                if st.button("🔄 Generate New Audio", use_container_width=True):
                    st.session_state.audio_path = None
                    st.rerun()
        else:
            st.error("Audio file not found!")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Groq AI, and Microsoft Edge TTS")
