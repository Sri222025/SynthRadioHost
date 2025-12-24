"""
Samaahar - Knowledge Spoken in Hinglish
Age-Appropriate AI Podcast Generator
"""

import streamlit as st
import os
import sys
import asyncio
import traceback
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Samaahar",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #0a2885;
        --secondary: #2563eb;
        --text: #1e293b;
        --gray: #64748b;
        --border: #e2e8f0;
    }
    
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { display: none; }
    
    .main .block-container {
        padding: 1.5rem !important;
        max-width: 680px !important;
    }
    
    h1 {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        text-align: center;
        margin-bottom: 0.3rem !important;
        letter-spacing: -0.5px;
    }
    
    h2 {
        color: var(--text) !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        margin: 1.5rem 0 1rem 0 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(10, 40, 133, 0.2) !important;
        width: 100% !important;
        font-size: 0.95rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(10, 40, 133, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .topic-card {
        background: white;
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 0.7rem;
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s;
    }
    
    .topic-card:hover {
        border-color: var(--secondary);
        box-shadow: 0 3px 10px rgba(37, 99, 235, 0.1);
    }
    
    .topic-card h3 {
        color: var(--primary);
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    
    .topic-card p {
        color: var(--gray);
        font-size: 0.88rem;
        line-height: 1.5;
        margin: 0;
    }
    
    .aud-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.9rem;
        margin: 1.2rem 0;
    }
    
    @media (max-width: 600px) {
        .aud-grid { grid-template-columns: 1fr; }
    }
    
    .aud-card {
        background: white;
        border: 2px solid var(--border);
        border-radius: 10px;
        padding: 1.3rem 0.9rem;
        text-align: center;
        transition: all 0.2s;
    }
    
    .aud-card:hover {
        border-color: var(--secondary);
        box-shadow: 0 3px 12px rgba(37, 99, 235, 0.12);
    }
    
    .aud-emoji { font-size: 2.3rem; margin-bottom: 0.4rem; }
    .aud-title { font-weight: 600; font-size: 1.05rem; color: var(--text); margin-bottom: 0.2rem; }
    .aud-age { font-size: 0.82rem; color: var(--gray); margin-bottom: 0.6rem; }
    .aud-desc { font-size: 0.82rem; color: var(--gray); line-height: 1.3; }
    
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid var(--border) !important;
        padding: 0.7rem !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(10, 40, 133, 0.08) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        color: var(--gray) !important;
    }
    
    audio {
        width: 100% !important;
        border-radius: 10px !important;
        margin: 0.8rem 0;
    }
    
    .stAlert { border-radius: 10px !important; }
    
    hr {
        margin: 1.8rem 0 !important;
        border: 0 !important;
        border-top: 1px solid var(--border) !important;
    }
    
    .tagline {
        text-align: center;
        color: var(--gray);
        font-size: 0.95rem;
        margin-top: 0.3rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    .caption {
        text-align: center;
        color: var(--gray);
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Imports
try:
    from src.wikipedia_handler import WikipediaHandler
    WIKI_OK = True
except:
    WIKI_OK = False

try:
    from src.script_generator import GroqScriptGenerator
    SCRIPT_OK = True
except:
    SCRIPT_OK = False

try:
    import edge_tts
    TTS_OK = True
except:
    TTS_OK = False

def check_groq_key() -> Optional[str]:
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")

def get_indian_voices(audience: str) -> tuple:
    """Get age-appropriate Indian English voices"""
    voice_map = {
        "Kids": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Teenagers": ("en-IN-AaravNeural", "en-IN-AashiNeural"),
        "Adults": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Elderly": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")
    }
    return voice_map.get(audience, ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"))

async def generate_audio_segment(text: str, voice: str, audience: str) -> bytes:
    """Generate age-appropriate audio with rate/pitch adjustments"""
    
    if audience == "Kids":
        rate = "+15%"
        pitch = "+10Hz"
    elif audience == "Teenagers":
        rate = "+10%"
        pitch = "+5Hz"
    elif audience == "Adults":
        rate = "+5%"
        pitch = "+0Hz"
    elif audience == "Elderly":
        rate = "-10%"
        pitch = "-5Hz"
    else:
        rate = "+0%"
        pitch = "+0Hz"
    
    if "*excited*" in text or "*laughs*" in text:
        rate_val = int(rate.replace('%', '').replace('+', '').replace('-', '')) + 5
        pitch_val = int(pitch.replace('Hz', '').replace('+', '').replace('-', '')) + 10
        rate = f"+{rate_val}%"
        pitch = f"+{pitch_val}Hz"
    elif "*sighs*" in text:
        rate = "-5%"
    
    clean_text = text.replace("*excited*", "").replace("*laughs*", "").replace("*chuckles*", "").replace("*sighs*", "").replace("*thoughtful*", "")
    
    communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
    audio_bytes = b""
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    
    return audio_bytes

def generate_podcast_audio(dialogue: List[Dict], audience: str) -> str:
    """Generate age-appropriate podcast audio"""
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        voice_male, voice_female = get_indian_voices(audience)
        audio_segments = []
        
        for idx, turn in enumerate(dialogue):
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            audio_bytes = asyncio.run(generate_audio_segment(text, voice, audience))
            audio_segments.append(audio_bytes)
            
            if idx < len(dialogue) - 1:
                pause_duration = 0.7 if audience == "Elderly" else 0.5
                audio_segments.append(b'\x00' * int(24000 * pause_duration * 2))
        
        combined = b"".join(audio_segments)
        
        output_path = output_dir / "podcast.mp3"
        with open(output_path, "wb") as f:
            f.write(combined)
        
        return str(output_path)
    except Exception as e:
        return None

# Session State
if 'step' not in st.session_state:
    st.session_state.step = 1
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

# Header
st.title("🎙️ Samaahar")
st.markdown("<p class='tagline'>Knowledge Spoken in Hinglish</p>", unsafe_allow_html=True)

# Only show system status on non-home screens (for debugging)
if st.session_state.step != 1:
    groq_key = check_groq_key()
    if not (groq_key and WIKI_OK and SCRIPT_OK and TTS_OK):
        with st.expander("⚙️ System Status", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write("✓ API" if groq_key else "✗ API")
            with col2:
                st.write("✓ Wiki" if WIKI_OK else "✗ Wiki")
            with col3:
                st.write("✓ AI" if SCRIPT_OK else "✗ AI")
            with col4:
                st.write("✓ TTS" if TTS_OK else "✗ TTS")

st.divider()

# STEP 1: Search
if st.session_state.step == 1:
    st.subheader("📚 Search Wikipedia")
    
    search_query = st.text_input("", placeholder="Enter topic: ISRO, Cricket, AI...", key="search_input", label_visibility="collapsed")
    
    if st.button("🔍 Search", type="primary"):
        if not search_query:
            st.warning("Please enter a topic")
        elif not WIKI_OK:
            st.error("Wikipedia unavailable")
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
                        st.warning("No results found")
                except Exception as e:
                    st.error(f"Search error: {str(e)}")

# STEP 2: Select Topic
elif st.session_state.step == 2:
    st.subheader(f"📝 Select Topic ({len(st.session_state.search_results)} results)")
    
    for idx, result in enumerate(st.session_state.search_results):
        st.markdown(f"""
        <div class="topic-card">
            <h3>{result.get('title', '')}</h3>
            <p>{result.get('description', '')[:110]}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Select", key=f"s_{idx}", use_container_width=True):
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

# STEP 3: Audience Selection
elif st.session_state.step == 3:
    st.subheader("🎯 Choose Your Audience")
    st.info(f"**Topic:** {st.session_state.selected_topic}")
    
    audiences = {
        "Kids": {"emoji": "🧒", "age": "6-12 years", "desc": "Fun, high-energy voices"},
        "Teenagers": {"emoji": "🎓", "age": "13-19 years", "desc": "Young, fast-paced voices"},
        "Adults": {"emoji": "👔", "age": "20-60 years", "desc": "Professional voices"},
        "Elderly": {"emoji": "👴", "age": "60+ years", "desc": "Clear, slower voices"}
    }
    
    st.markdown('<div class="aud-grid">', unsafe_allow_html=True)
    
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
            
            if st.button(f"{aud}", key=f"a_{aud}", use_container_width=True):
                st.session_state.config = {
                    "audience": aud,
                    "style": "Conversational",
                    "duration": 2
                }
                st.session_state.step = 4
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("← Change Topic"):
        st.session_state.step = 1
        st.session_state.selected_topic = None
        st.session_state.wiki_content = None
        st.rerun()

# STEP 4: Generate Script
elif st.session_state.step == 4:
    config = st.session_state.config
    groq_key = check_groq_key()
    
    if not st.session_state.script_data:
        st.subheader("🎬 Generating Script...")
        st.info(f"**Topic:** {st.session_state.selected_topic} | **Audience:** {config['audience']}")
        
        if not SCRIPT_OK or not groq_key:
            st.error("AI service unavailable. Please check system configuration.")
            if st.button("← Go Back"):
                st.session_state.step = 3
                st.rerun()
        else:
            with st.spinner(f"Creating {config['audience']}-friendly script... (30-60 seconds)"):
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
                        st.rerun()
                    else:
                        error_msg = result.get('error', 'Unknown error')
    
                   if "Rate limit" in error_msg:
                       st.warning(f"⏳ {error_msg}")
                       st.info("💡 **Tip:** The free tier has limits. Trying again in a moment usually works!")
                   else:
                       st.error(f"❌ {error_msg}")
    
                       col1, col2 = st.columns(2)
                   with col1:
                        if st.button("🔄 Retry Now"):
                            st.session_state.step = 4
                            st.rerun()
                   with col2:
                        if st.button("← Change Audience"):
                            st.session_state.step = 3
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                        if st.button("← Go Back"):
                           st.session_state.step = 3
                           st.rerun()
    
    else:
        st.subheader("📄 Your Hinglish Script")
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
            for turn in data["dialogue"]:
                speaker = turn.get("speaker", "")
                text = turn.get("text", "")
                emoji = "🙋‍♂️" if speaker == "Rajesh" else "🙋‍♀️"
                st.markdown(f"{emoji} **{speaker}:** {text}")
                st.markdown("")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Regenerate Script"):
                st.session_state.script_data = None
                st.session_state.audio_path = None
                st.rerun()
        with col2:
            if st.button("🎤 Generate Audio", type="primary"):
                st.session_state.step = 5
                st.rerun()

# STEP 5: Generate Audio
elif st.session_state.step == 5:
    
    if not st.session_state.audio_path:
        st.subheader("🎵 Generating Audio...")
        st.info(f"Creating {st.session_state.config['audience']}-appropriate voices...")
        
        if not TTS_OK:
            st.error("Text-to-Speech service unavailable")
            if st.button("← Back to Script"):
                st.session_state.step = 4
                st.rerun()
        else:
            with st.spinner(f"Generating natural audio... (1-2 minutes)"):
                try:
                    dialogue = st.session_state.script_data.get("dialogue", [])
                    audience = st.session_state.config.get("audience", "Adults")
                    
                    audio_path = generate_podcast_audio(dialogue, audience)
                    
                    if audio_path:
                        st.session_state.audio_path = audio_path
                        st.rerun()
                    else:
                        st.error("Audio generation failed")
                        if st.button("← Try Again"):
                            st.session_state.step = 4
                            st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    if st.button("← Go Back"):
                        st.session_state.step = 4
                        st.rerun()
    
    else:
        st.subheader("✅ Your Podcast is Ready!")
        
        with open(st.session_state.audio_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            
            size = len(audio_bytes) / (1024 * 1024)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("File Size", f"{size:.1f} MB")
            with col2:
                st.metric("Voice Style", st.session_state.config['audience'])
            
            st.download_button(
                "⬇️ Download MP3",
                audio_bytes,
                f"{st.session_state.selected_topic.replace(' ', '_')}_samaahar.mp3",
                "audio/mp3",
                use_container_width=True
            )
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Audio"):
                    st.session_state.audio_path = None
                    st.session_state.step = 5
                    st.rerun()
            with col2:
                if st.button("🏠 Create New Podcast"):
                    st.session_state.step = 1
                    st.session_state.selected_topic = None
                    st.session_state.wiki_content = None
                    st.session_state.config = None
                    st.session_state.script_data = None
                    st.session_state.audio_path = None
                    st.rerun()

# Footer
st.divider()
st.markdown("<p class='caption'>Powered by Groq AI & Microsoft Edge TTS</p>", unsafe_allow_html=True)
