"""
Synth Radio Host - Wikipedia to Hinglish Podcast
Jio-Inspired Clean Design | Mobile-First | 2-Person Conversation
"""

import streamlit as st
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional
from pydub import AudioSegment
import edge_tts
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="centered",  # Centered for mobile-first
    initial_sidebar_state="collapsed"  # Hidden sidebar for clean look
)

# Import modules
try:
    from src.wikipedia_handler import WikipediaHandler
    WIKI_OK = True
except Exception as e:
    WIKI_OK = False
    wiki_error = str(e)

try:
    from src.script_generator import ScriptGenerator
    SCRIPT_OK = True
except Exception as e:
    SCRIPT_OK = False
    script_error = str(e)


# ============================================
# JIO-INSPIRED DESIGN SYSTEM
# ============================================

st.markdown("""
<style>
    /* Jio Color Palette */
    :root {
        --jio-blue: #0a2885;
        --jio-light-blue: #1e40af;
        --jio-bg: #f8fafc;
        --jio-card: #ffffff;
        --jio-text: #1e293b;
        --jio-text-light: #64748b;
        --jio-success: #10b981;
        --jio-error: #ef4444;
    }
    
    /* Global Styles */
    .stApp {
        background-color: var(--jio-bg);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography - Jio Style */
    h1, h2, h3 {
        color: var(--jio-blue) !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, var(--jio-blue) 0%, var(--jio-light-blue) 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(10, 40, 133, 0.15);
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        color: white;
    }
    
    /* Progress Steps - Jio Style */
    .progress-container {
        display: flex;
        justify-content: space-between;
        margin: 1.5rem 0;
        padding: 0 1rem;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .progress-step::after {
        content: '';
        position: absolute;
        top: 20px;
        left: 50%;
        width: 100%;
        height: 2px;
        background: #e2e8f0;
        z-index: -1;
    }
    
    .progress-step:last-child::after {
        display: none;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 3px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        color: var(--jio-text-light);
        margin-bottom: 0.5rem;
    }
    
    .step-circle.active {
        background: var(--jio-blue);
        border-color: var(--jio-blue);
        color: white;
    }
    
    .step-circle.completed {
        background: var(--jio-success);
        border-color: var(--jio-success);
        color: white;
    }
    
    .step-label {
        font-size: 0.75rem;
        color: var(--jio-text-light);
        text-align: center;
    }
    
    /* Cards - Jio Style */
    .jio-card {
        background: var(--jio-card);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .jio-card:hover {
        box-shadow: 0 4px 16px rgba(10, 40, 133, 0.12);
        transform: translateY(-2px);
    }
    
    .topic-card {
        cursor: pointer;
        position: relative;
    }
    
    .topic-card:hover {
        border-color: var(--jio-blue);
    }
    
    .topic-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--jio-text);
        margin-bottom: 0.5rem;
    }
    
    .topic-snippet {
        font-size: 0.9rem;
        color: var(--jio-text-light);
        line-height: 1.5;
    }
    
    /* Buttons - Jio Style */
    .stButton > button {
        background: var(--jio-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(10, 40, 133, 0.2);
    }
    
    .stButton > button:hover {
        background: var(--jio-light-blue);
        box-shadow: 0 6px 20px rgba(10, 40, 133, 0.3);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Button */
    .stButton.secondary > button {
        background: white;
        color: var(--jio-blue);
        border: 2px solid var(--jio-blue);
    }
    
    .stButton.secondary > button:hover {
        background: var(--jio-bg);
    }
    
    /* Input Fields - Jio Style */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--jio-blue);
        box-shadow: 0 0 0 3px rgba(10, 40, 133, 0.1);
    }
    
    /* Radio Buttons - Jio Style */
    .stRadio > div {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .stRadio > div > label {
        background: white;
        padding: 0.75rem 1.25rem;
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.3s ease;
        flex: 1;
        min-width: 120px;
        text-align: center;
    }
    
    .stRadio > div > label:hover {
        border-color: var(--jio-blue);
        background: var(--jio-bg);
    }
    
    .stRadio > div > label[data-checked="true"] {
        background: var(--jio-blue);
        color: white;
        border-color: var(--jio-blue);
    }
    
    /* Select Box - Jio Style */
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* Slider - Jio Style */
    .stSlider > div > div > div {
        background: var(--jio-blue);
    }
    
    /* Text Area - Jio Style */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        font-family: 'Courier New', monospace;
    }
    
    /* Info/Success/Error Boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem;
    }
    
    /* Audio Player */
    audio {
        width: 100%;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .badge-blue {
        background: rgba(10, 40, 133, 0.1);
        color: var(--jio-blue);
    }
    
    .badge-green {
        background: rgba(16, 185, 129, 0.1);
        color: var(--jio-success);
    }
    
    /* Dialogue Display */
    .dialogue-turn {
        background: var(--jio-bg);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 4px solid var(--jio-blue);
    }
    
    .speaker-name {
        font-weight: 700;
        color: var(--jio-blue);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .dialogue-text {
        color: var(--jio-text);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.5rem;
        }
        
        .progress-container {
            padding: 0 0.5rem;
        }
        
        .step-circle {
            width: 32px;
            height: 32px;
            font-size: 0.8rem;
        }
        
        .step-label {
            font-size: 0.65rem;
        }
        
        .jio-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# HELPER FUNCTIONS
# ============================================

def check_groq_key():
    """Check for Groq API key"""
    try:
        return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        return os.getenv("GROQ_API_KEY")


def get_voices_for_audience(audience: str) -> tuple:
    """Get Indian voice pair for audience"""
    # Using Indian English voices for authentic Hinglish
    voice_map = {
        "Kids (5-12)": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Teenagers (13-18)": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Adults (19-60)": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"),
        "Elderly (60+)": ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural")
    }
    return voice_map.get(audience, ("en-IN-PrabhatNeural", "en-IN-NeerjaNeural"))


async def generate_audio_segment(text: str, voice: str) -> bytes:
    """Generate audio for a single segment"""
    communicate = edge_tts.Communicate(text, voice)
    audio_bytes = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]
    return audio_bytes


def mix_dialogue_audio(dialogue: list, voice_male: str, voice_female: str) -> str:
    """Mix 2-person dialogue into single audio file"""
    try:
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Combine all audio segments
        combined_audio = AudioSegment.empty()
        
        for turn in dialogue:
            speaker = turn.get("speaker", "Rajesh")
            text = turn.get("text", "")
            
            # Select voice based on speaker
            voice = voice_male if speaker == "Rajesh" else voice_female
            
            # Generate audio for this turn
            audio_bytes = asyncio.run(generate_audio_segment(text, voice))
            
            # Convert to AudioSegment
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            
            # Add to combined audio
            combined_audio += audio_segment
            
            # Add pause between turns (300ms)
            combined_audio += AudioSegment.silent(duration=300)
        
        # Export final audio
        output_path = output_dir / "podcast.mp3"
        combined_audio.export(output_path, format="mp3")
        
        return str(output_path)
    
    except Exception as e:
        raise Exception(f"Audio mixing failed: {str(e)}")


def render_progress_steps(current_step: int):
    """Render Jio-style progress indicator"""
    steps = ["Search", "Select", "Configure", "Script", "Audio"]
    
    html = '<div class="progress-container">'
    for i, step in enumerate(steps, 1):
        if i < current_step:
            circle_class = "completed"
            icon = "✓"
        elif i == current_step:
            circle_class = "active"
            icon = str(i)
        else:
            circle_class = ""
            icon = str(i)
        
        html += f'''
        <div class="progress-step">
            <div class="step-circle {circle_class}">{icon}</div>
            <div class="step-label">{step}</div>
        </div>
        '''
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


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
if 'config' not in st.session_state:
    st.session_state.config = {}
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None


# ============================================
# HEADER
# ============================================

st.markdown('''
<div class="header-card">
    <div class="header-title">🎙️ Synth Radio Host</div>
    <div class="header-subtitle">Wikipedia se Hinglish Podcast banao - Instantly!</div>
</div>
''', unsafe_allow_html=True)

# Progress indicator
render_progress_steps(st.session_state.step)


# ============================================
# STEP 1: SEARCH WIKIPEDIA
# ============================================

if st.session_state.step == 1:
    st.markdown("### 🔍 Koi bhi topic search karo")
    
    # System status check
    groq_key = check_groq_key()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if groq_key and WIKI_OK and SCRIPT_OK:
            st.success("✅ All systems ready!")
        else:
            if not groq_key:
                st.error("❌ GROQ_API_KEY missing")
            if not WIKI_OK:
                st.error(f"❌ Wikipedia: {wiki_error}")
            if not SCRIPT_OK:
                st.error("❌ Script Generator not available")
    
    with col2:
        st.markdown('<span class="badge badge-blue">Free</span><span class="badge badge-green">Fast</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Search input
    search_keyword = st.text_input(
        "Topic ka naam likho (Hindi/English)",
        placeholder="jaise: Mumbai Indians, Cricket, Bollywood, Technology...",
        key="search_input",
        label_visibility="collapsed"
    )
    
    if st.button("🔎 Search Wikipedia", use_container_width=True):
        if not search_keyword.strip():
            st.error("❌ Kuch toh likho yaar!")
        elif not WIKI_OK:
            st.error("❌ Wikipedia connection failed!")
        else:
            with st.spinner("🔍 Searching Wikipedia..."):
                wiki = WikipediaHandler()
                results = wiki.search_topics(search_keyword, limit=10)
                
                if results:
                    st.session_state.search_results = results
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("❌ Koi result nahi mila. Kuch aur try karo!")


# ============================================
# STEP 2: SELECT TOPIC
# ============================================

elif st.session_state.step == 2:
    st.markdown(f"### ✅ {len(st.session_state.search_results)} topics mile!")
    st.caption("Apna favorite select karo")
    
    st.markdown("---")
    
    for idx, result in enumerate(st.session_state.search_results):
        st.markdown(f'''
        <div class="jio-card topic-card">
            <div class="topic-title">{result['title']}</div>
            <div class="topic-snippet">{result['snippet']}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"Select →", key=f"select_{idx}", use_container_width=True):
            with st.spinner(f"📖 Loading '{result['title']}'..."):
                wiki = WikipediaHandler()
                content = wiki.get_article_content(result['title'], max_chars=3000)
                
                st.session_state.selected_topic = result['title']
                st.session_state.wiki_content = content
                st.session_state.step = 3
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("← Wapas jao", key="back_step1"):
        st.session_state.step = 1
        st.rerun()


# ============================================
# STEP 3: CONFIGURE
# ============================================

elif st.session_state.step == 3:
    st.markdown(f"### ⚙️ Podcast setup karo")
    st.success(f"📚 Topic: **{st.session_state.selected_topic}**")
    
    with st.expander("📖 Wikipedia preview dekho"):
        st.write(st.session_state.wiki_content['summary'])
        st.caption(f"[Full article padho]({st.session_state.wiki_content['url']})")
    
    st.markdown("---")
    
    # Configuration form
    st.markdown("#### 🎯 Audience kaun hai?")
    audience = st.radio(
        "Kiske liye banao?",
        options=["Kids (5-12)", "Teenagers (13-18)", "Adults (19-60)", "Elderly (60+)"],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⏱️ Duration")
        duration = st.slider(
            "Kitne minute?",
            min_value=2,
            max_value=10,
            value=2,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("#### 🎨 Style")
        style = st.selectbox(
            "Kaise present karna hai?",
            options=["Conversational", "Educational", "Entertaining", "Informative"],
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Preview config
    st.info(f"🎙️ **2 log baat karenge** (Rajesh & Priya) | 🗣️ **Hinglish mix** | ⏱️ **{duration} minutes**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Change Topic", use_container_width=True, key="back_step2"):
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            # Save config
            st.session_state.config = {
                'audience': audience,
                'duration': duration,
                'style': style
            }
            
            groq_key = check_groq_key()
            if not groq_key:
                st.error("❌ GROQ_API_KEY not configured!")
            elif not SCRIPT_OK:
                st.error("❌ Script generator not available!")
            else:
                with st.spinner(f"🤖 {duration}-minute Hinglish script ban raha hai..."):
                    try:
                        generator = ScriptGenerator(api_key=groq_key)
                        
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
                            st.success("✅ Script ready hai!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Kuch gadbad hui: {str(e)}")


# ============================================
# STEP 4: SCRIPT REVIEW
# ============================================

elif st.session_state.step == 4:
    script_data = st.session_state.script_data
    
    st.markdown(f"### 📻 {script_data.get('title', 'Your Podcast')}")
    
    # Metadata badges
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<span class="badge badge-blue">{st.session_state.config["audience"].split("(")[0].strip()}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<span class="badge badge-blue">{st.session_state.config["duration"]} min</span>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="badge badge-green">Hinglish</span>', unsafe_allow_html=True)
    
    if script_data.get('description'):
        st.info(script_data['description'])
    
    st.markdown("---")
    
    # Adaptations
    if script_data.get('key_adaptations'):
        with st.expander("🎯 Kaise adapt kiya humne"):
            for adaptation in script_data['key_adaptations']:
                st.write(f"✓ {adaptation}")
    
    # Dialogue display
    st.markdown("#### 💬 Conversation Preview")
    
    dialogue = script_data.get('dialogue', [])
    if dialogue:
        for turn in dialogue[:6]:  # Show first 6 turns
            speaker = turn.get('speaker', 'Host')
            text = turn.get('text', '')
            
            st.markdown(f'''
            <div class="dialogue-turn">
                <div class="speaker-name">{speaker}:</div>
                <div class="dialogue-text">{text}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        if len(dialogue) > 6:
            with st.expander(f"📋 Baaki {len(dialogue) - 6} dialogues dekho"):
                for turn in dialogue[6:]:
                    speaker = turn.get('speaker', 'Host')
                    text = turn.get('text', '')
                    st.markdown(f"**{speaker}:** {text}")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Script phir se banao", use_container_width=True, key="regenerate"):
            with st.spinner("🔄 Naya script ban raha hai..."):
                try:
                    groq_key = check_groq_key()
                    generator = ScriptGenerator(api_key=groq_key)
                    
                    result = generator.generate_script(
                        wikipedia_content=st.session_state.wiki_content['full_text'],
                        topic_title=st.session_state.selected_topic,
                        duration_minutes=st.session_state.config['duration'],
                        style=st.session_state.config['style'],
                        audience=st.session_state.config['audience'],
                        regenerate=True  # More variety
                    )
                    
                    if result.get("success"):
                        st.session_state.script_data = result
                        st.session_state.audio_path = None
                        st.success("✅ Naya script ready!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("🎤 Audio banao", type="primary", use_container_width=True, key="generate_audio"):
            st.session_state.step = 5
            st.rerun()


# ============================================
# STEP 5: AUDIO GENERATION
# ============================================

elif st.session_state.step == 5:
    script_data = st.session_state.script_data
    
    st.markdown(f"### 🎵 Audio Generation")
    
    if not st.session_state.audio_path:
        st.info("🎙️ Rajesh aur Priya ki awaaz mein podcast ban raha hai...")
        
        try:
            with st.spinner("🎵 Audio generate ho raha hai... (1-2 minutes lag sakte hain)"):
                # Get voices
                audience = st.session_state.config['audience']
                voice_male, voice_female = get_voices_for_audience(audience)
                
                # Generate and mix audio
                dialogue = script_data.get('dialogue', [])
                audio_path = mix_dialogue_audio(dialogue, voice_male, voice_female)
                
                st.session_state.audio_path = audio_path
                st.success("✅ Audio ready hai!")
                st.balloons()
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Audio generation failed: {str(e)}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Phir se try karo", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("← Script par wapas jao", use_container_width=True):
                    st.session_state.step = 4
                    st.rerun()
    
    else:
        # Audio ready - display player
        st.success("✅ Aapka podcast ready hai!")
        
        audio_path = Path(st.session_state.audio_path)
        if audio_path.exists():
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            # Audio player
            st.audio(audio_bytes, format="audio/mp3")
            
            # File info
            file_size_mb = len(audio_bytes) / (1024 * 1024)
            st.caption(f"📊 Size: {file_size_mb:.2f} MB | 🎙️ Voices: Rajesh & Priya")
            
            # Download button
            st.download_button(
                label="⬇️ Download karo (MP3)",
                data=audio_bytes,
                file_name=f"{st.session_state.selected_topic.replace(' ', '_')}.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Navigation
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Script change karo", use_container_width=True):
                    st.session_state.step = 4
                    st.session_state.audio_path = None
                    st.rerun()
            
            with col2:
                if st.button("← Naya topic", use_container_width=True):
                    # Reset everything
                    st.session_state.step = 1
                    st.session_state.search_results = []
                    st.session_state.selected_topic = None
                    st.session_state.wiki_content = None
                    st.session_state.config = {}
                    st.session_state.script_data = None
                    st.session_state.audio_path = None
                    st.rerun()
        
        else:
            st.error("❌ Audio file nahi mili!")


# ============================================
# FOOTER
# ============================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: var(--jio-text-light); padding: 1rem; font-size: 0.85rem;">
    <p>🏆 <strong>Hackathon Project 2025</strong></p>
    <p>Built with ❤️ | Groq AI + Microsoft Edge TTS + Wikipedia</p>
    <p><strong>USP:</strong> 2-Person Hinglish Conversations with Audience Adaptation</p>
</div>
""", unsafe_allow_html=True)
