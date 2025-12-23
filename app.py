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
    st.error(f"⚠️ ScriptGenerator import failed: {e}")
    SCRIPT_GEN_AVAILABLE = False
    ScriptGenerator = None

try:
    from src.tts_engine_mock import MockTTSEngine
    TTS_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ TTS Engine not available: {e}")
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
        border-color: #FF5252;
    }
    .status-box {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }
    .error-box {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
    }
    .info-box {
        background-color: #D1ECF1;
        border: 1px solid #BEE5EB;
        color: #0C5460;
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
    if 'generation_error' not in st.session_state:
        st.session_state.generation_error = None

def check_api_key() -> Optional[str]:
    """Check for Gemini API key in environment or secrets"""
    # Try Streamlit secrets first
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass
    
    # Try environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    return None

def display_system_status():
    """Display system component status"""
    with st.sidebar:
        st.subheader("🔧 System Status")
        
        # API Key status
        api_key = check_api_key()
        if api_key:
            st.success("✅ Gemini API Key: Configured")
        else:
            st.error("❌ Gemini API Key: Missing")
            st.info("💡 Add GEMINI_API_KEY to Streamlit Secrets")
        
        # Script Generator status
        if SCRIPT_GEN_AVAILABLE:
            st.success("✅ Script Generator: Ready")
        else:
            st.error("❌ Script Generator: Not Available")
        
        # TTS Engine status
        if TTS_AVAILABLE:
            st.success("✅ TTS Engine: Ready (Mock)")
        else:
            st.warning("⚠️ TTS Engine: Not Available")
        
        st.divider()

def generate_script(topic: str, duration: int, style: str) -> Dict[str, Any]:
    """Generate podcast script using Gemini API"""
    try:
        if not SCRIPT_GEN_AVAILABLE:
            return {
                "success": False,
                "error": "Script Generator not available. Check imports."
            }
        
        api_key = check_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "GEMINI_API_KEY not found. Please configure in Streamlit Secrets."
            }
        
        # Initialize generator
        generator = ScriptGenerator(api_key=api_key)
        
        # Generate script
        with st.spinner(f"🤖 Generating {duration}-minute {style} script about '{topic}'..."):
            result = generator.generate_script(
                topic=topic,
                duration_minutes=duration,
                style=style
            )
        
        return result
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Script generation failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def generate_audio(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate audio from script using TTS engine"""
    try:
        if not TTS_AVAILABLE or not MockTTSEngine:
            return {
                "success": False,
                "error": "TTS Engine not available"
            }
        
        # Initialize TTS engine
        tts_engine = MockTTSEngine()
        
        # Create output directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        # Generate audio file
        output_path = output_dir / "podcast.wav"
        
        with st.spinner("🎵 Generating audio (this may take a moment)..."):
            # Combine all script segments
            full_text = "\n\n".join([
                f"{seg.get('speaker', 'Host')}: {seg.get('text', '')}"
                for seg in script_data.get('segments', [])
            ])
            
            # Generate speech
            audio_path = tts_engine.synthesize(
                text=full_text,
                output_path=str(output_path)
            )
        
        return {
            "success": True,
            "audio_path": audio_path
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Audio generation failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

def main():
    """Main application logic"""
    init_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎙️ Synth Radio Host</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Podcast Generator</div>', unsafe_allow_html=True)
    
    # Display system status in sidebar
    display_system_status()
    
    # Sidebar - Input controls
    with st.sidebar:
        st.header("📝 Podcast Configuration")
        
        topic = st.text_input(
            "Topic",
            value="The Future of AI",
            help="What should the podcast be about?"
        )
        
        duration = st.slider(
            "Duration (minutes)",
            min_value=1,
            max_value=30,
            value=5,
            help="How long should the podcast be?"
        )
        
        style = st.selectbox(
            "Style",
            options=["Informative", "Conversational", "Educational", "Entertaining", "News"],
            help="What tone should the podcast have?"
        )
        
        st.divider()
        
        generate_btn = st.button("🚀 Generate Podcast Script", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📄 Generated Script")
        
        # Script generation
        if generate_btn:
            if not topic.strip():
                st.error("❌ Please enter a topic!")
            else:
                # Reset previous state
                st.session_state.script_generated = False
                st.session_state.audio_generated = False
                st.session_state.generation_error = None
                
                # Generate script
                result = generate_script(topic, duration, style)
                
                if result.get("success"):
                    st.session_state.script_generated = True
                    st.session_state.script_data = result
                    st.success("✅ Script generated successfully!")
                else:
                    st.session_state.generation_error = result.get("error", "Unknown error")
                    st.error(f"❌ {st.session_state.generation_error}")
                    
                    # Show detailed error if available
                    if "traceback" in result:
                        with st.expander("🔍 Error Details"):
                            st.code(result["traceback"], language="python")
        
        # Display script
        if st.session_state.script_generated and st.session_state.script_data:
            script_data = st.session_state.script_data
            
            # Display title
            if "title" in script_data:
                st.markdown(f"### {script_data['title']}")
            
            # Display script content
            if "script" in script_data:
                st.text_area(
                    "Script Content",
                    value=script_data["script"],
                    height=400,
                    key="script_display"
                )
            
            # Display segments if available
            if "segments" in script_data:
                st.markdown("#### Script Segments")
                for i, segment in enumerate(script_data["segments"], 1):
                    with st.expander(f"Segment {i}: {segment.get('speaker', 'Host')}"):
                        st.write(f"**Duration:** {segment.get('duration', 0)} seconds")
                        st.write(segment.get('text', ''))
        
        elif st.session_state.generation_error:
            st.info("👆 Fix the errors above and try generating again")
    
    with col2:
        st.subheader("🎵 Audio Generation")
        
        if st.session_state.script_generated:
            if st.button("🎤 Generate Audio", key="generate_audio_btn"):
                result = generate_audio(st.session_state.script_data)
                
                if result.get("success"):
                    st.session_state.audio_generated = True
                    st.session_state.audio_path = result["audio_path"]
                    st.success("✅ Audio generated!")
                else:
                    st.error(f"❌ {result.get('error', 'Audio generation failed')}")
                    if "traceback" in result:
                        with st.expander("🔍 Error Details"):
                            st.code(result["traceback"], language="python")
            
            if st.session_state.audio_generated and st.session_state.audio_path:
                # Display audio player
                if Path(st.session_state.audio_path).exists():
                    with open(st.session_state.audio_path, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=audio_bytes,
                        file_name="podcast.wav",
                        mime="audio/wav"
                    )
                else:
                    st.error("❌ Audio file not found")
        else:
            st.info("👈 Generate a script first to enable audio generation")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Built with ❤️ using Streamlit and Google Gemini AI</p>
        <p>🎙️ Create engaging podcasts in minutes</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
