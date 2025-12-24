"""
Synth Radio Host - AI Podcast Generator
Mobile-First Design - No Sidebar
Audience Adaptation is the PRIMARY USP
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

# Mobile-First CSS - Jio Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    :root {
        --jio-blue: #0a2885;
        --jio-light-blue: #2563eb;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Mobile-first padding */
    .main .block-container {
        padding: 1rem !important;
        max-width: 800px !important;
    }
    
    h1 {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        text-align: center;
    }
    
    @media (min-width: 768px) {
        h1 { font-size: 2.5rem !important; }
    }
    
    h2 {
        color: var(--jio-blue) !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--jio-blue), var(--jio-light-blue)) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.875rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(10, 40, 133, 0.3) !important;
        width: 100% !important;
        font-size: 1rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(10, 40, 133, 0.5) !important;
    }
    
    /* Cards */
    .topic-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 2px solid #e2e8f0;
        transition: all 0.3s;
    }
    
    .topic-card:hover {
        border-color: var(--jio-light-blue);
        box-shadow: 0 4px 16px rgba(10, 40, 133, 0.15);
    }
    
    /* Audience cards */
    .audience-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 3px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    
    .audience-card:hover {
        border-color: var(--jio-light-blue);
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(10, 40, 133, 0.2);
    }
    
    .audience-card.selected {
        border-color: var(--jio-blue);
        background: linear-gradient(135deg, #e0f2fe, #dbeafe);
        box-shadow: 0 8px 24px rgba(10, 40, 133, 0.3);
    }
    
    /* Input */
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--jio-blue) !important;
        box-shadow: 0 0 0 3px rgba(10, 40, 133, 0.1) !important;
    }
    
    /* Radio buttons - Large touch targets */
    .stRadio > div {
        gap: 1rem;
    }
    
    .stRadio > div > label {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--jio-light-blue);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    /* Audio player */
    audio {
        width: 100% !important;
        border-radius: 12px !important;
        margin: 1rem 0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-ok {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0 !important;
        border: 0 !important;
        border-top: 2px solid #e2e8f0 !important;
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
    """Get Indian English voices with better quality"""
    voice_map = {
        "Kids": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Teenagers": ("en-IN-AaravNeural", "en-IN-NeerjaNeural"),
        "Adults": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Elderly": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")
    }
    return voice_map.get(audience, ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"))

async def generate_audio_segment_with_emotion(text: str, voice: str, speaker: str) -> bytes:
    """Generate audio with prosody and emotions for human-like speech"""
    
    # Add SSML for natural speech
    # Detect emotions from text markers
    rate = "+0%"  # Normal speed
    pitch = "+0Hz"  # Normal pitch
    
    if "*excited*" in text or "*laughs*" in text:
        rate = "+10%"
        pitch = "+20Hz"
    elif "*sighs*" in text or "*thoughtful*" in text:
        rate = "-5%"
        pitch = "-10Hz"
    
    # Clean text of emotion markers for speech
    clean_text = text.replace("*excited*", "").replace("*laughs*", "").replace("*chuckles*", "").replace("*sighs*", "").replace("*thoughtful*", "")
    
    # Create SSML with prosody
    ssml_text = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="hi-IN">
        <prosody rate="{rate}" pitch="{pitch}">
            {clean_text}
        </prosody>
    </speak>
    """
    
    communicate = edge_tts.Communicate(clean_text, voice, rate=rate, pitch=pitch)
    audio_bytes = b""
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    
    return audio_bytes

def generate_podcast_audio(dialogue: List[Dict], audience: str) -> str:
    """Generate natural-sounding audio with pauses between speakers"""
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        voice_male, voice_female = get_indian_voices(audience)
        
        audio_segments = []
        
        for idx, turn in enumerate(dialogue):
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            # Generate with emotion
            audio_bytes = asyncio.run(generate_audio_segment_with_emotion(text, voice, speaker))
            audio_segments.append(audio_bytes)
            
            # Add 0.5 second pause between speakers (silence)
            if idx < len(dialogue) - 1:
                pause_duration = 0.5  # seconds
                sample_rate = 24000
                silence = b'\x00' * int(sample_rate * pause_duration * 2)  # 16-bit audio
                audio_segments.append(silence)
        
        # Combine all audio
        combined_audio = b"".join(audio_segments)
        
        output_path = output_dir / "podcast.mp3"
        with open(output_path, "wb") as f:
            f.write(combined_audio)
        
        return str(output_path)
    
    except Exception as e:
        st.error(f"Audio error: {str(e)}")
        return None

# Initialize Session State
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None
if 'wiki_content' not in st.session_state:
    st.session_state.wiki_content = None
if 'audience_selected' not in st.session_state:
    st.session_state.audience_selected = False
if 'config' not in st.session_state:
    st.session_state.config = None
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# === HEADER ===
st.title("🎙️ Synth Radio Host")
st.caption("Wikipedia se Hinglish Podcast | Audience-Adapted AI Radio")

# System Status (compact)
groq_key = check_groq_key()
st.markdown(f"""
<div style="text-align: center; margin: 1rem 0;">
    <span class="status-badge {'status-ok' if groq_key else 'status-error'}">{'✅' if groq_key else '❌'} API</span>
    <span class="status-badge {'status-ok' if WIKI_OK else 'status-error'}">{'✅' if WIKI_OK else '❌'} Wikipedia</span>
    <span class="status-badge {'status-ok' if SCRIPT_OK else 'status-error'}">{'✅' if SCRIPT_OK else '❌'} AI</span>
    <span class="status-badge {'status-ok' if TTS_OK else 'status-error'}">{'✅' if TTS_OK else '❌'} TTS</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# === STEP 1: Search ===
if not st.session_state.selected_topic:
    st.subheader("📚 Step 1: खोजें Topic")
    
    search_query = st.text_input(
        "Wikipedia पर कोई भी topic खोजें",
        placeholder="जैसे: ISRO, Cricket, Bollywood, AI...",
        key="search_input"
    )
    
    if st.button("🔍 Search", use_container_width=True, type="primary"):
        if not search_query:
            st.warning("⚠️ कृपया topic enter करें")
        elif not WIKI_OK:
            st.error("❌ Wikipedia not available!")
        else:
            with st.spinner("🔍 Searching..."):
                try:
                    wiki = WikipediaHandler()
                    results = wiki.search_topics(search_query, limit=10)
                    
                    if results:
                        st.session_state.search_results = results
                        st.success(f"✅ {len(results)} topics मिले!")
                    else:
                        st.warning("⚠️ कोई topic नहीं मिला")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# === STEP 2: Select Topic ===
if st.session_state.search_results and not st.session_state.selected_topic:
    st.divider()
    st.subheader(f"📝 Step 2: Topic चुनें ({len(st.session_state.search_results)} results)")
    
    for idx, result in enumerate(st.session_state.search_results):
        st.markdown(f"""
        <div class="topic-card">
            <h3>📄 {result.get('title', 'Unknown')}</h3>
            <p style="color: #64748b; font-size: 0.9rem;">{result.get('description', '')[:150]}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        select_key = f"sel_{idx}_{result.get('title', idx)[:10]}"
        if st.button(f"✔️ यह topic चुनें", key=select_key, use_container_width=True):
            with st.spinner("📄 Loading..."):
                try:
                    wiki = WikipediaHandler()
                    content = wiki.get_article_content(result['title'], max_chars=5000)
                    
                    if content:
                        st.session_state.selected_topic = result['title']
                        st.session_state.wiki_content = content
                        st.session_state.search_results = []
                        st.rerun()
                    else:
                        st.error("❌ Content नहीं मिला")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# === STEP 3: Audience Selection (PRIMARY USP!) ===
if st.session_state.selected_topic and not st.session_state.audience_selected:
    st.divider()
    st.subheader("🎯 Step 3: Audience चुनें")
    st.info(f"**Selected Topic:** {st.session_state.selected_topic}")
    
    st.markdown("### किसके लिए podcast बनाना है?")
    
    # Audience options with emoji
    audiences = {
        "Kids": {"emoji": "🧒", "desc": "6-12 साल | सरल भाषा, मजेदार examples"},
        "Teenagers": {"emoji": "🎓", "desc": "13-19 साल | Cool slang, trendy style"},
        "Adults": {"emoji": "👔", "desc": "20-60 साल | Professional, detailed"},
        "Elderly": {"emoji": "👴", "desc": "60+ साल | आदरपूर्ण, धीमी गति"}
    }
    
    selected_audience = None
    
    for audience, info in audiences.items():
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{info['emoji']}</h1>", unsafe_allow_html=True)
        
        with col2:
            if st.button(f"**{audience}**\n\n{info['desc']}", key=f"aud_{audience}", use_container_width=True):
                selected_audience = audience
    
    if selected_audience:
        st.markdown("### अब style चुनें:")
        style = st.radio(
            "Conversation का tone कैसा हो?",
            ["Informative", "Conversational", "Educational"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        duration = st.slider("Duration (minutes)", 1, 5, 2)
        
        if st.button("✅ Continue to Script", type="primary", use_container_width=True):
            st.session_state.config = {
                "audience": selected_audience,
                "style": style,
                "duration": duration
            }
            st.session_state.audience_selected = True
            st.rerun()

# === STEP 4: Generate Script ===
if st.session_state.audience_selected and not st.session_state.script_data:
    st.divider()
    st.subheader("🎬 Step 4: Script Generate करें")
    
    config = st.session_state.config
    
    st.info(f"""
    **Topic:** {st.session_state.selected_topic}  
    **Audience:** {config['audience']} | **Style:** {config['style']} | **Duration:** ~{config['duration']} min
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            if not SCRIPT_OK or not groq_key:
                st.error("❌ AI not available!")
            else:
                with st.spinner(f"✨ {config['audience']} के लिए Hinglish script बना रहे हैं... (30-60s)"):
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
                            st.success("✅ Script ready!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {result.get('error')}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("⬅️ Change Audience", use_container_width=True):
            st.session_state.audience_selected = False
            st.rerun()

# === STEP 5: Display Script ===
if st.session_state.script_data:
    st.divider()
    st.subheader("📄 Your Hinglish Script")
    
    data = st.session_state.script_data
    config = st.session_state.config
    
    if "title" in data:
        st.markdown(f"### 🎙️ {data['title']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥", "Rajesh & Priya")
    with col2:
        st.metric("⏱️", f"~{config['duration']} min")
    with col3:
        st.metric("🎯", config['audience'])
    
    st.divider()
    
    if "dialogue" in data:
        st.markdown("#### 💬 Conversation:")
        
        for turn in data["dialogue"]:
            speaker = turn.get("speaker", "")
            text = turn.get("text", "")
            
            if speaker == "Rajesh":
                st.markdown(f"**🙋‍♂️ {speaker}:** {text}")
            else:
                st.markdown(f"**🙋‍♀️ {speaker}:** {text}")
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.divider()
    
    # Regenerate button (FIXED - doesn't reset to home)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate Script", use_container_width=True):
            st.session_state.script_data = None
            st.session_state.audio_path = None
            # DON'T reset audience_selected or config
            st.rerun()
    
    with col2:
        if st.button("⬅️ New Topic", use_container_width=True):
            # Reset everything
            st.session_state.selected_topic = None
            st.session_state.wiki_content = None
            st.session_state.audience_selected = False
            st.session_state.config = None
            st.session_state.script_data = None
            st.session_state.audio_path = None
            st.rerun()

# === STEP 6: Generate Audio ===
if st.session_state.script_data:
    st.divider()
    st.subheader("🎵 Step 5: Audio Generate करें")
    
    if not st.session_state.audio_path:
        if st.button("🎤 Generate Podcast Audio", type="primary", use_container_width=True):
            if not TTS_OK:
                st.error("❌ TTS not available!")
            else:
                with st.spinner("🎙️ Natural-sounding audio बना रहे हैं... (1-2 min)"):
                    try:
                        dialogue = st.session_state.script_data.get("dialogue", [])
                        audience = st.session_state.config.get("audience", "Adults")
                        
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
            st.success("✅ आपका podcast तैयार है!")
            
            with open(st.session_state.audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                
                file_size = len(audio_bytes) / (1024 * 1024)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 Size: {file_size:.2f} MB")
                with col2:
                    st.info(f"🎙️ {st.session_state.config['audience']} Voice")
                
                st.download_button(
                    label="⬇️ Download MP3",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}_podcast.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
                if st.button("🔄 Regenerate Audio", use_container_width=True):
                    st.session_state.audio_path = None
                    st.rerun()

# Footer
st.divider()
st.caption("Built with ❤️ | Powered by Groq AI & Microsoft Edge TTS")
st.caption("🎯 USP: Audience-Adapted Hinglish Podcasts")
