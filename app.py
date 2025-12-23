"""
Synth Radio Host - Wikipedia to Podcast Generator
Hackathon Version with Audience Adaptation
"""

import streamlit as st
import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports with error handling
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

try:
    from src.tts_engine_mock import MockTTSEngine
    TTS_OK = True
except Exception as e:
    TTS_OK = False
    tts_error = str(e)

# Custom CSS
st.markdown("""
<style>
    .topic-card {
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .topic-card:hover {
        border-color: #FF6B6B;
        box-shadow: 0 2px 8px rgba(255,107,107,0.2);
    }
    .selected-topic {
        border-color: #FF6B6B;
        background-color: #fff5f5;
    }
</style>
""", unsafe_allow_html=True)

def check_api_key():
    """Check for API key"""
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except:
        return os.getenv("GEMINI_API_KEY")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1=Search, 2=Select, 3=Configure, 4=Generated
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

# Header
st.title("🎙️ Synth Radio Host")
st.caption("Wikipedia to Podcast - AI-Powered with Audience Adaptation")

# Sidebar - System Status
with st.sidebar:
    st.header("🔧 System Status")
    
    api_key = check_api_key()
    st.success("✅ API Key" if api_key else "❌ API Key Missing")
    st.success("✅ Wikipedia" if WIKI_OK else f"❌ Wikipedia: {wiki_error if not WIKI_OK else ''}")
    st.success("✅ Script Gen" if SCRIPT_OK else f"❌ Script: {script_error if not SCRIPT_OK else ''}")
    st.success("✅ TTS Engine" if TTS_OK else "⚠️ TTS: Mock Mode")
    
    st.divider()
    
    # Progress indicator
    st.header("📍 Progress")
    steps = ["🔍 Search", "✅ Select Topic", "⚙️ Configure", "🎵 Generate"]
    for i, step_name in enumerate(steps, 1):
        if i < st.session_state.step:
            st.success(f"{step_name} ✓")
        elif i == st.session_state.step:
            st.info(f"**→ {step_name}**")
        else:
            st.text(step_name)

# Main content area
if st.session_state.step == 1:
    # STEP 1: SEARCH WIKIPEDIA
    st.header("🔍 Step 1: Search Wikipedia Topics")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_keyword = st.text_input(
            "Enter search keyword",
            placeholder="e.g., Artificial Intelligence, Climate Change, Space Exploration",
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
                results = wiki.search_topics(search_keyword, limit=30)
                
                if results:
                    st.session_state.search_results = results
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("❌ No topics found. Try a different keyword.")

elif st.session_state.step == 2:
    # STEP 2: SELECT TOPIC
    st.header("✅ Step 2: Select a Topic")
    
    st.info(f"📚 Found {len(st.session_state.search_results)} topics related to your search")
    
    for idx, result in enumerate(st.session_state.search_results):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.subheader(result['title'])
                st.caption(result['snippet'])
            
            with col2:
                st.write("")
                if st.button("Select →", key=f"select_{idx}", use_container_width=True):
                    with st.spinner(f"📖 Fetching '{result['title']}'..."):
                        wiki = WikipediaHandler()
                        content = wiki.get_article_content(result['title'], max_chars=2500)
                        
                        st.session_state.selected_topic = result['title']
                        st.session_state.wiki_content = content
                        st.session_state.step = 3
                        st.rerun()
            
            st.divider()
    
    if st.button("← Back to Search"):
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 3:
    # STEP 3: CONFIGURE & GENERATE
    st.header("⚙️ Step 3: Configure Your Podcast")
    
    # Show selected topic
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
            key="audience_select"
        )
        
        st.info(f"**USP**: Script will be adapted specifically for {audience} with appropriate vocabulary, examples, and tone!")
    
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
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Podcast Script", type="primary", use_container_width=True, key="generate_btn"):
            if not SCRIPT_OK:
                st.error("❌ Script generator not available!")
            elif not api_key:
                st.error("❌ API key not configured!")
            else:
                with st.spinner(f"🤖 Generating {duration}-min {style} podcast for {audience}..."):
                    try:
                        generator = ScriptGenerator(api_key=api_key)
                        result = generator.generate_script(
                            wikipedia_content=st.session_state.wiki_content['full_text'],
                            topic_title=st.session_state.selected_topic,
                            duration_minutes=duration,
                            style=style,
                            audience=audience
                        )
                        
                        if result.get("success"):
                            st.session_state.script_data = result
                            st.session_state.audio_path = None  # Reset audio
                            st.session_state.step = 4
                            st.success("✅ Script generated successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result.get('error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    if st.button("← Change Topic"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 4:
    # STEP 4: SCRIPT GENERATED
    st.header("📄 Generated Podcast Script")
    
    script_data = st.session_state.script_data
    
    # Show metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic", st.session_state.selected_topic)
    with col2:
        st.metric("Audience", script_data.get('target_audience', 'N/A'))
    with col3:
        st.metric("Duration", f"{script_data.get('total_duration', 0)//60} min")
    
    st.divider()
    
    # Show script
    col_script, col_audio = st.columns([2, 1])
    
    with col_script:
        st.subheader(f"📻 {script_data.get('title', 'Podcast Script')}")
        
        if script_data.get('description'):
            st.info(script_data['description'])
        
        # Show key adaptations (USP)
        if script_data.get('key_adaptations'):
            with st.expander("🎯 Audience Adaptations (Our USP!)"):
                for adaptation in script_data['key_adaptations']:
                    st.write(f"• {adaptation}")
        
        # Show full script
        st.text_area(
            "Full Script",
            value=script_data.get("script", ""),
            height=400,
            key="script_display"
        )
        
        # Show segments
        if script_data.get('segments'):
            st.markdown("#### 📋 Script Breakdown")
            for i, seg in enumerate(script_data['segments'], 1):
                with st.expander(f"Segment {i}: {seg.get('type', 'main').title()} ({seg.get('duration')}s)"):
                    st.write(seg.get('text', ''))
                    if seg.get('notes'):
                        st.caption(f"💡 {seg['notes']}")
        
        # Regenerate button
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
                
                st.audio(audio_bytes, format="audio/wav")
                
                st.download_button(
                    label="⬇️ Download Podcast",
                    data=audio_bytes,
                    file_name=f"{st.session_state.selected_topic.replace(' ', '_')}.wav",
                    mime="audio/wav",
                    use_container_width=True
                )
        else:
            st.info("Click below to generate audio from the script")
            
            if st.button("🎤 Generate Audio", type="primary", use_container_width=True):
                if not TTS_OK:
                    st.error("❌ TTS engine not available!")
                else:
                    try:
                        with st.spinner("🎵 Generating audio... This may take a moment"):
                            tts = MockTTSEngine()
                            
                            Path("outputs").mkdir(exist_ok=True)
                            
                            # Combine script segments
                            segments = script_data.get('segments', [])
                            full_text = "\n\n".join([
                                seg.get('text', '') for seg in segments
                            ])
                            
                            # Generate audio
                            audio_file = tts.synthesize(
                                text=full_text,
                                output_path=f"outputs/{st.session_state.selected_topic.replace(' ', '_')}.wav"
                            )
                            
                            st.session_state.audio_path = audio_file
                            st.success("✅ Audio generated!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Audio generation failed: {str(e)}")
        
        st.divider()
        
        # Navigation
        if st.button("🔄 Regenerate Script", use_container_width=True):
            st.session_state.step = 3
            st.session_state.audio_path = None
            st.rerun()
        
        if st.button("← New Topic", use_container_width=True):
            st.session_state.step = 1
            st.session_state.search_results = []
            st.session_state.selected_topic = None
            st.session_state.script_data = None
            st.session_state.audio_path = None
            st.rerun()

# Footer
st.divider()
st.caption("🏆 Hackathon Project | Built with ❤️ using Streamlit, Wikipedia API & Google Gemini AI")
st.caption("**USP**: Audience-adapted scripts with vocabulary, complexity, and tone matching target demographics")
