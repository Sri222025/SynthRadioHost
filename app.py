"""
Synth Radio Host - AI-Powered Podcast Generator
Streamlit application for generating radio show scripts and audio
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
import traceback

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import custom modules with error handling
try:
    from src.script_generator import ScriptGenerator
    SCRIPT_GEN_AVAILABLE = True
except ImportError as e:
    SCRIPT_GEN_AVAILABLE = False
    ScriptGenerator = None

try:
    from src.tts_engine_mock import MockTTSEngine
    TTS_AVAILABLE = True
except ImportError as e:
    TTS_AVAILABLE = False
    MockTTSEngine = None

# Page configuration
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF5252;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'script_generated' not in st.session_state:
        st.session_state.script_generated = False
    if 'script_data' not in st.session_state:
        st.session_state.script_data = None
    if 'audio_generated' not in st.session_state:
        st.session_state.audio_generated = False
    if 'audio_path' not in st.session_state:
        st.session_state.audio_path = None

def check_api_key() -> Optional[str]:
    """Check for Gemini API key"""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass
    
    api_key = os.getenv("GEMINI_API_KEY")
    return api_key

def main():
    """Main application logic"""
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎙️ Synth Radio Host</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Podcast Generator</div>', unsafe_allow_html=True)
    
    # ===== SIDEBAR: STEP 1 - CONFIGURE =====
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Check system components
        api_key = check_api_key()
        if api_key:
            st.success("✅ API Key: Configured")
        else:
            st.error("❌ API Key: Missing")
            st.info("💡 Add GEMINI_API_KEY to Streamlit Secrets")
        
        if SCRIPT_GEN_AVAILABLE:
            st.success("✅ Script Generator: Ready")
        else:
            st.error("❌ Script Generator: Not Available")
        
        if TTS_AVAILABLE:
            st.success("✅ TTS Engine: Ready")
        else:
            st.warning("⚠️ TTS Engine: Not Available")
        
        st.divider()
        
        # ===== INPUT CONTROLS =====
        st.header("📝 Step 1: Configure Podcast")
        
        topic = st.text_input(
            "📌 Topic",
            value="The Future of Artificial Intelligence",
            help="What should the podcast be about?",
            key="topic_input"
        )
        
        duration = st.slider(
            "⏱️ Duration (minutes)",
            min_value=1,
            max_value=15,
            value=3,
            help="Target podcast length",
            key="duration_slider"
        )
        
        style = st.selectbox(
            "🎨 Style",
            options=["Informative", "Conversational", "Educational", "Entertaining", "News"],
            index=0,
            help="Tone and approach",
            key="style_select"
        )
        
        st.divider()
        
        # ===== GENERATE BUTTON =====
        st.header("🚀 Step 2: Generate")
        generate_btn = st.button(
            "🎬 Generate Podcast Script",
            type="primary",
            use_container_width=True,
            key="generate_button"
        )
    
    # ===== MAIN AREA: DISPLAY RESULTS =====
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Generated Script")
        
        # Handle script generation
        if generate_btn:
            if not topic.strip():
                st.error("❌ Please enter a topic!")
            elif not SCRIPT_GEN_AVAILABLE:
                st.error("❌ Script generator not available. Check imports.")
            elif not api_key:
                st.error("❌ GEMINI_API_KEY not configured!")
            else:
                # Reset state
                st.session_state.script_generated = False
                st.session_state.audio_generated = False
                
                try:
                    # Generate script
                    with st.spinner(f"🤖 Generating {duration}-min {style} script about '{topic}'..."):
                        generator = ScriptGenerator(api_key=api_key)
                        result = generator.generate_script(
                            topic=topic,
                            duration_minutes=duration,
                            style=style
                        )
                    
                    if result.get("success"):
                        st.session_state.script_generated = True
                        st.session_state.script_data = result
                        st.success("✅ Script generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
        
        # Display generated script
        if st.session_state.script_generated and st.session_state.script_data:
            script_data = st.session_state.script_data
            
            # Show title
            if "title" in script_data:
                st.markdown(f"### 📻 {script_data['title']}")
            
            # Show description
            if "description" in script_data:
                st.info(script_data['description'])
            
            # Show script text
            if "script" in script_data:
                st.text_area(
                    "Full Script",
                    value=script_data["script"],
                    height=400,
                    key="script_display"
                )
            
            # Show segments
            if "segments" in script_data and len(script_data["segments"]) > 0:
                st.markdown("#### 📋 Script Segments")
                for i, segment in enumerate(script_data["segments"], 1):
                    with st.expander(f"Segment {i}: {segment.get('type', 'main').title()} ({segment.get('duration', 0)}s)"):
                        st.write(f"**Speaker:** {segment.get('speaker', 'Host')}")
                        st.write(segment.get('text', ''))
        else:
            st.info("👈 Configure your podcast in the sidebar and click 'Generate Podcast Script'")
    
    with col2:
        st.subheader("🎵 Step 3: Audio Generation")
        
        if st.session_state.script_generated:
            if st.button("🎤 Generate Audio", type="primary", use_container_width=True, key="audio_button"):
                if not TTS_AVAILABLE:
                    st.error("❌ TTS Engine not available")
                else:
                    try:
                        with st.spinner("🎵 Generating audio..."):
                            tts = MockTTSEngine()
                            
                            # Create output directory
                            output_dir = Path("outputs")
                            output_dir.mkdir(exist_ok=True)
                            output_path = output_dir / "podcast.wav"
                            
                            # Combine script text
                            segments = st.session_state.script_data.get('segments', [])
                            full_text = "\n\n".join([
                                f"{seg.get('speaker', 'Host')}: {seg.get('text', '')}"
                                for seg in segments
                            ])
                            
                            # Generate audio
                            audio_file = tts.synthesize(full_text, str(output_path))
                            
                            st.session_state.audio_generated = True
                            st.session_state.audio_path = audio_file
                            st.success("✅ Audio generated!")
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Audio generation failed: {str(e)}")
            
            # Display audio player
            if st.session_state.audio_generated and st.session_state.audio_path:
                audio_path = Path(st.session_state.audio_path)
                if audio_path.exists():
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    
                    st.audio(audio_bytes, format="audio/wav")
                    st.download_button(
                        label="⬇️ Download Podcast",
                        data=audio_bytes,
                        file_name="podcast.wav",
                        mime="audio/wav",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Audio file not found")
        else:
            st.info("👈 Generate a script first to enable audio generation")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Built with ❤️ using Streamlit and Google Gemini AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
