"""
Synth Radio Host - Wikipedia to Podcast Generator
Hackathon Version with Audience Adaptation
Multi-Model Support: Groq (Primary) + Gemini (Backup)
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
    from src.groq_script_generator import GroqScriptGenerator
    GROQ_OK = True
except Exception as e:
    GROQ_OK = False
    groq_error = str(e)

try:
    from src.script_generator import ScriptGenerator
    GEMINI_OK = True
except Exception as e:
    GEMINI_OK = False
    gemini_error = str(e)

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
    .api-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 0.25rem 0;
    }
    .groq-badge {
        background-color: #f4a261;
        color: white;
    }
    .gemini-badge {
        background-color: #4285f4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Check for available API keys"""
    groq_key = None
    gemini_key = None
    
    try:
        groq_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    except:
        groq_key = os.getenv("GROQ_API_KEY")
    
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except:
        gemini_key = os.getenv("GEMINI_API_KEY")
    
    return groq_key, gemini_key

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
if 'used_api' not in st.session_state:
    st.session_state.used_api = None

# Header
st.title("🎙️ Synth Radio Host")
st.caption("Wikipedia to Podcast - AI-Powered with Audience Adaptation")

# Sidebar - System Status
with st.sidebar:
    st.header("🔧 System Status")
    
    groq_key, gemini_key = check_api_keys()
    
    # API Status
    if groq_key and GROQ_OK:
        st.success("✅ Groq API (Primary) - Llama 3.3 70B")
    elif groq_key:
        st.warning(f"⚠️ Groq API: {groq_error if not GROQ_OK else 'Error'}")
    else:
        st.info("💡 Add GROQ_API_KEY for faster generation")
    
    if gemini_key and GEMINI_OK:
        st.success("✅ Gemini API (Backup)")
    elif gemini_key:
        st.warning(f"⚠️ Gemini API: {gemini_error if not GEMINI_OK else 'Error'}")
    else:
        st.info("💡 Add GEMINI_API_KEY as backup")
    
    # Other components
    if WIKI_OK:
        st.success("✅ Wikipedia API")
    else:
        st.error(f"❌ Wikipedia: {wiki_error if not WIKI_OK else 'Error'}")
    
    if TTS_OK:
        st.success("✅ TTS Engine (Mock)")
    else:
        st.warning("⚠️ TTS: Not available")
    
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
    
    st.divider()
    
    # API Info
    with st.expander("ℹ️ About APIs"):
        st.markdown("""
        **Groq (Recommended)**
        - 🚀 Super fast (2-5 seconds)
        - 🆓 14,400 requests/day free
        - 🧠 Llama 3.3 70B model
        - Sign up: console.groq.com
        
        **Gemini (Backup)**
        - 🤖 Google's AI model
        - 🆓 Limited free tier
        - Sign up: aistudio.google.com
        """)

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
                results = wiki.search_topics(search_keyword, limit=10)
                
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
        
        st.info(f"**🎯 USP**: Script will be adapted specifically for {audience} with appropriate vocabulary, examples, and tone!")
    
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
    
    # API Selection info
    groq_key, gemini_key = check_api_keys()
    
    if groq_key and GROQ_OK:
        st.info("🚀 Will use **Groq (Llama 3.3 70B)** - Super fast generation!")
    elif gemini_key and GEMINI_OK:
        st.info("🤖 Will use **Gemini** - Good quality generation")
    else:
        st.error("❌ No API key configured! Please add GROQ_API_KEY or GEMINI_API_KEY to Streamlit Secrets")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Podcast Script", type="primary", use_container_width=True, key="generate_btn")
    
    if generate_btn:
        if not groq_key and not gemini_key:
            st.error("❌ No API key configured! Add GROQ_API_KEY or GEMINI_API_KEY to secrets.")
        else:
            with st.spinner(f"🤖 Generating {duration}-min {style} podcast for {audience}..."):
                try:
                    # Prefer Groq if available (faster + higher quota)
                    if groq_key and GROQ_OK:
                        st.info("🚀 Using Groq API (Llama 3.3 70B) - Lightning fast!")
                        generator = GroqScriptGenerator(api_key=groq_key)
                        st.session_state.used_api = "Groq"
                    elif gemini_key and GEMINI_OK:
                        st.info("🤖 Using Gemini API")
                        generator = ScriptGenerator(api_key=gemini_key)
                        st.session_state.used_api = "Gemini"
                    else:
                        st.error("❌ No working API available!")
                        st.stop()
                    
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
                        st.success(f"✅ Script generated successfully using {st.session_state.used_api}!")
                        st.balloons()
                        st.rerun()
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        st.error(f"❌ Generation failed: {error_msg}")
                        
                        # Show helpful suggestions
                        if "quota" in error_msg.lower():
                            st.warning("💡 **Suggestion**: Try using Groq API instead (much higher free quota)")
                            st.info("Sign up at: https://console.groq.com/")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
    
    if st.button("← Change Topic"):
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 4:
    # STEP 4: SCRIPT GENERATED
    st.header("📄 Generated Podcast Script")
    
    script_data = st.session_state.script_data
    
    # Show metadata with API badge
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Topic", st.session_state.selected_topic)
    with col2:
        st.metric("Audience", script_data.get('target_audience', 'N/A'))
    with col3:
        st.metric("Duration", f"{script_data.get('total_duration', 0)//60} min")
    with col4:
        api_used = st.session_state.used_api or "Unknown"
        badge_class = "groq-badge" if api_used == "Groq" else "gemini-badge"
        st.markdown(f'<div class="api-badge {badge_class}">Generated by {api_used}</div>', unsafe_allow_html=True)
    
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
                st.markdown("**How we adapted this content for your target audience:**")
                for adaptation in script_data['key_adaptations']:
                    st.write(f"✓ {adaptation}")
        
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
                segment_type = seg.get('type', 'main').title()
                segment_duration = seg.get('duration', 0)
                
                with st.expander(f"Segment {i}: {segment_type} ({segment_duration}s)"):
                    st.write(seg.get('text', ''))
                    if seg.get('notes'):
                        st.caption(f"💡 **Note:** {seg['notes']}")
        
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
                
                st.caption(f"📊 File size: {len(audio_bytes) / 1024:.1f} KB")
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
                            safe_filename = st.session_state.selected_topic.replace(' ', '_').replace('/', '-')
                            audio_file = tts.synthesize(
                                text=full_text,
                                output_path=f"outputs/{safe_filename}.wav"
                            )
                            
                            st.session_state.audio_path = audio_file
                            st.success("✅ Audio generated!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Audio generation failed: {str(e)}")
                        with st.expander("🔍 Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
        
        st.divider()
        
        # Navigation
        if st.button("🔄 New Configuration", use_container_width=True, key="regen_config"):
            st.session_state.step = 3
            st.session_state.audio_path = None
            st.rerun()
        
        if st.button("← New Topic", use_container_width=True):
            st.session_state.step = 1
            st.session_state.search_results = []
            st.session_state.selected_topic = None
            st.session_state.script_data = None
            st.session_state.audio_path = None
            st.session_state.used_api = None
            st.rerun()

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: #666;">🏆 <strong>Hackathon Project</strong></p>
        <p style="color: #999; font-size: 0.9rem;">Built with ❤️ using Streamlit, Wikipedia API & AI</p>
        <p style="color: #999; font-size: 0.85rem;"><strong>USP:</strong> Audience-adapted scripts with vocabulary, complexity, and tone matching target demographics</p>
    </div>
    """, unsafe_allow_html=True)
