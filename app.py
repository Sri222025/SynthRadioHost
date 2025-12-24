"""
Synth Radio Host - AI Podcast Generator
Professional Mobile-First Design
Audience Adaptation USP
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

# Page config
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional Mobile-First CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --jio-blue: #0a2885;
        --jio-light: #2563eb;
        --accent: #06b6d4;
        --success: #10b981;
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #1e293b;
        --gray: #64748b;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        display: none;
    }
    
    .main .block-container {
        padding: 1.5rem !important;
        max-width: 700px !important;
    }
    
    h1 {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    h3 {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Professional Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0a2885 0%, #2563eb 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(10, 40, 133, 0.25) !important;
        width: 100% !important;
        font-size: 0.95rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 16px rgba(10, 40, 133, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Clean Topic Cards */
    .topic-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
    }
    
    .topic-card:hover {
        border-color: var(--jio-light);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }
    
    .topic-card h3 {
        color: var(--jio-blue);
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }
    
    .topic-card p {
        color: var(--gray);
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Modern Audience Grid */
    .audience-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    @media (max-width: 600px) {
        .audience-grid {
            grid-template-columns: 1fr;
        }
    }
    
    .aud-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .aud-card:hover {
        border-color: var(--jio-light);
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.15);
        transform: scale(1.02);
    }
    
    .aud-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .aud-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--text);
        margin-bottom: 0.25rem;
    }
    
    .aud-age {
        font-size: 0.85rem;
        color: var(--gray);
        margin-bottom: 0.75rem;
    }
    
    .aud-desc {
        font-size: 0.85rem;
        color: var(--gray);
        line-height: 1.4;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--jio-blue) !important;
        box-shadow: 0 0 0 3px rgba(10, 40, 133, 0.1) !important;
    }
    
    /* Slider */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Status Badges */
    .status-row {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-ok {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: var(--jio-blue) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: var(--gray) !important;
    }
    
    /* Audio Player */
    audio {
        width: 100% !important;
        border-radius: 10px !important;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border: 0 !important;
        border-top: 1px solid #e2e8f0 !important;
    }
    
    /* Caption */
    .caption-text {
        text-align: center;
        color: var(--gray);
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Import modules
try:
    from src.wikipedia_handler import WikipediaHandler
    WIKI_OK = True
except Exception as e:
    WIKI_OK = False

try:
    from src.script_generator import GroqScriptGenerator
    SCRIPT_OK = True
except Exception as e:
    SCRIPT_OK = False

try:
    import edge_tts
    TTS_OK = True
except Exception as e:
    TTS_OK = False

# Helper Functions
def check_groq_key() -> Optional[str]:
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")

def get_indian_voices(audience: str) -> tuple:
    voice_map = {
        "Kids": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Teenagers": ("en-IN-AaravNeural", "en-IN-NeerjaNeural"),
        "Adults": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Elderly": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")
    }
    return voice_map.get(audience, ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"))

async def generate_audio_segment_with_emotion(text: str, voice: str) -> bytes:
    rate = "+5%"
    pitch = "+0Hz"
    
    if "*excited*" in text or "*laughs*" in text:
        rate = "+15%"
        pitch = "+15Hz"
    elif "*sighs*" in text:
        rate = "-5%"
        pitch = "-10Hz"
    
    clean_text = text.replace("*excited*", "").replace("*laughs*", "").replace("*chuckles*", "").replace("*sighs*", "")
    
    communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
    audio_bytes = b""
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    
    return audio_bytes

def generate_podcast_audio(dialogue: List[Dict], audience: str) -> str:
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        voice_male, voice_female = get_indian_voices(audience)
        audio_segments = []
        
        for idx, turn in enumerate(dialogue):
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            audio_bytes = asyncio.run(generate_audio_segment_with_emotion(text, voice))
            audio_segments.append(audio_bytes)
            
            if idx < len(dialogue) - 1:
                silence = b'\x00' * int(24000 * 0.5 * 2)
                audio_segments.append(silence)
        
        combined_audio = b"".join(audio_segments)
        
        output_path = output_dir / "podcast.mp3"
        with open(output_path, "wb") as f:
            f.write(combined_audio)
        
        return str(output_path)
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None

# Initialize Session State - CRITICAL FIX
if 'step' not in st.session_state:
    st.session_state.step = 1  # Track current step
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None
if 'wiki_content' not in st.session_state:
    st.session_state.wiki_content = None
if 'config' not in st.session_state:
    st.session_state.config = None
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# === HEADER ===
st.title("🎙️ Synth Radio Host")
st.markdown("<p class='caption-text'>Wikipedia se Hinglish Podcast | Audience-Adapted</p>", unsafe_allow_html=True)

# System Status
groq_key = check_groq_key()
st.markdown(f"""
<div class="status-row">
    <span class="badge {'badge-ok' if groq_key else 'badge-error'}">{'✓' if groq_key else '✗'} API</span>
    <span class="badge {'badge-ok' if WIKI_OK else 'badge-error'}">{'✓' if WIKI_OK else '✗'} Wiki</span>
    <span class="badge {'badge-ok' if SCRIPT_OK else 'badge-error'}">{'✓' if SCRIPT_OK else '✗'} AI</span>
    <span class="badge {'badge-ok' if TTS_OK else 'badge-error'}">{'✓' if TTS_OK else '✗'} TTS</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# === STEP 1: Search ===
if st.session_state.step == 1:
    st.subheader("📚 Search Wikipedia Topic")
    
    search_query = st.text_input(
        "",
        placeholder="Enter topic: ISRO, Cricket, Bollywood, AI...",
        key="search_input",
        label_visibility="collapsed"
    )
    
    if st.button("🔍 Search", type="primary"):
        if not search_query:
            st.warning("Please enter a topic")
        elif not WIKI_OK:
            st.error("Wikipedia not available")
        else:
            with st.spinner("Searching..."):
                try:
                    wiki = WikipediaHandler()
                    results = wiki.search_topics(search_query, limit=10)
                    
                    if results:
                        st.session_state.search_results = results
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.warning("No topics found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# === STEP 2: Select Topic ===
elif st.session_state.step == 2:
    st.subheader(f"📝 Select Topic ({len(st.session_state.search_results)} results)")
    
    for idx, result in enumerate(st.session_state.search_results):
        st.markdown(f"""
        <div class="topic-card">
            <h3>{result.get('title', 'Unknown')}</h3>
            <p>{result.get('description', '')[:120]}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select", key=f"sel_{idx}", use_container_width=True):
            with st.spinner("Loading content..."):
                try:
                    wiki = WikipediaHandler()
                    content = wiki.get_article_content(result['title'], max_chars=5000)
                    
                    if content:
                        st.session_state.selected_topic = result['title']
                        st.session_state.wiki_content = content
                        st.session_state.search_results = []
                        st.session_state.step = 3
                        st.rerun()
                    else:
                        st.error("Could not fetch content")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if st.button("← Back to Search"):
        st.session_state.step = 1
        st.session_state.search_results = []
        st.rerun()

# === STEP 3: Select Audience ===
elif st.session_state.step == 3:
    st.subheader("🎯 Choose Your Audience")
    st.info(f"**Topic:** {st.session_state.selected_topic}")
    
    audiences = {
        "Kids": {"emoji": "🧒", "age": "6-12 years", "desc": "Simple words, fun examples"},
        "Teenagers": {"emoji": "🎓", "age": "13-19 years", "desc": "Modern slang, trendy style"},
        "Adults": {"emoji": "👔", "age": "20-60 years", "desc": "Professional, detailed"},
        "Elderly": {"emoji": "👴", "age": "60+ years", "desc": "Clear, respectful, slow-paced"}
    }
    
    st.markdown('<div class="audience-grid">', unsafe_allow_html=True)
    
    cols = st.columns(2)
    for idx, (aud, info) in enumerate(audiences.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="aud-card">
                <div class="aud-emoji">{info['emoji']}</div>
                <div class="aud-title">{aud}</div>
                <div class="aud-age">{info['age']}</div>
                <div class="aud-desc">{info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Choose {aud}", key=f"aud_{aud}", use_container_width=True):
                st.session_state.config = {"audience": aud, "style": "Conversational"}
                st.session_state.step = 4
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("← Change Topic"):
        st.session_state.step = 1
        st.session_state.selected_topic = None
        st.session_state.wiki_content = None
        st.rerun()

# === STEP 4: Set Duration ===
elif st.session_state.step == 4:
    st.subheader("⏱️ Podcast Duration")
    st.info(f"**Topic:** {st.session_state.selected_topic} | **Audience:** {st.session_state.config['audience']}")
    
    duration = st.slider("How many minutes?", 1, 5, 2, key="dur_slider")
    
    st.session_state.config['duration'] = duration
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Change Audience"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Continue →", type="primary"):
            st.session_state.step = 5
            st.rerun()

# === STEP 5: Generate Script ===
elif st.session_state.step == 5:
    st.subheader("🎬 Generate Script")
    
    config = st.session_state.config
    st.info(f"**Topic:** {st.session_state.selected_topic} | **Audience:** {config['audience']} | **Duration:** {config['duration']} min")
    
    if not st.session_state.script_data:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Generate Script", type="primary", use_container_width=True):
                if not SCRIPT_OK or not groq_key:
                    st.error("AI not available")
                else:
                    with st.spinner(f"Generating {config['audience']} script... (30-60s)"):
                        try:
                            generator = GroqScriptGenerator(api_key=groq_key)
                            wiki_text = str(st.session_state.wiki_content)[:3000]
                            
                            result = generator.generate_script(
                                topic=st.session_state.selected_topic,
                                wikipedia_content=wiki_text,
                                duration_minutes=config["duration"],
                                style=config["style"],
                                audience=config["audience"]
                            )
                            
                            if result.get("success"):
                                st.session_state.script_data = result
                                st.success("Script ready!")
                                st.rerun()
                            else:
                                st.error(f"Failed: {result.get('error')}")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("← Back", use_container_width=True):
                st.session_state.step = 4
                st.rerun()
    
    else:
        # Display Script
        data = st.session_state.script_data
        
        if "title" in data:
            st.markdown(f"### 🎙️ {data['title']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Speakers", "2")
        with col2:
            st.metric("Duration", f"~{config['duration']} min")
        with col3:
            st.metric("Audience", config['audience'])
        
        st.divider()
        
        if "dialogue" in data:
            st.markdown("**Conversation:**")
            for turn in data["dialogue"]:
                speaker = turn.get("speaker", "")
                text = turn.get("text", "")
                emoji = "🙋‍♂️" if speaker == "Rajesh" else "🙋‍♀️"
                st.markdown(f"{emoji} **{speaker}:** {text}")
                st.markdown("")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.script_data = None
                st.session_state.audio_path = None
                st.rerun()
        with col2:
            if st.button("🎤 Generate Audio →", type="primary", use_container_width=True):
                st.session_state.step = 6
                st.rerun()

# === STEP 6: Generate Audio ===
elif st.session_state.step == 6:
    st.subheader("🎵 Generate Audio")
    
    if not st.session_state.audio_path:
        if st.button("🎤 Generate Podcast Audio", type="primary", use_container_width=True):
            if not TTS_OK:
                st.error("TTS not available")
            else:
                with st.spinner("Creating natural audio... (1-2 min)"):
                    try:
                        dialogue = st.session_state.script_data.get("dialogue", [])
                        audience = st.session_state.config.get("audience", "Adults")
                        
                        audio_path = generate_podcast_audio(dialogue, audience)
                        
                        if audio_path:
                            st.session_state.audio_path = audio_path
                            st.success("Audio ready!")
                            st.rerun()
                        else:
                            st.error("Audio generation failed")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.button("← Back to Script"):
            st.session_state.step = 5
            st.rerun()
    
    else:
        if Path(st.session_state.audio_path).exists():
            st.success("Your podcast is ready!")
            
            with open(st.session_state.audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                file_size = len(audio_bytes) / (1024 * 1024)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("File Size", f"{file_size:.1f} MB")
                with col2:
                    st.metric("Voice", f"{st.session_state.config['audience']}")
                
                st.download_button(
                    "⬇️ Download MP3",
                    audio_bytes,
                    f"{st.session_state.selected_topic.replace(' ', '_')}_podcast.mp3",
                    "audio/mp3",
                    use_container_width=True
                )
                
                st.divider()
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 New Audio", use_container_width=True):
                        st.session_state.audio_path = None
                        st.rerun()
                with col2:
                    if st.button("🏠 Start Over", use_container_width=True):
                        # Reset everything
                        st.session_state.step = 1
                        st.session_state.selected_topic = None
                        st.session_state.wiki_content = None
                        st.session_state.config = None
                        st.session_state.script_data = None
                        st.session_state.audio_path = None
                        st.rerun()

# Footer
st.divider()
st.markdown("<p class='caption-text'>Built with ❤️ | Groq AI & Microsoft Edge TTS</p>", unsafe_allow_html=True)
st.markdown("<p class='caption-text'>USP: Audience-Adapted Hinglish Podcasts</p>", unsafe_allow_html=True)
