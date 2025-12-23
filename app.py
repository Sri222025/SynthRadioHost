"""Synth Radio Host - Minimal Working Version"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Synth Radio Host",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import with safety checks
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

def check_api_key():
    """Check for API key"""
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except:
        return os.getenv("GEMINI_API_KEY")

# Initialize state
if 'script_data' not in st.session_state:
    st.session_state.script_data = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# Header
st.title("🎙️ Synth Radio Host")
st.caption("AI-Powered Podcast Generator")

# Sidebar
with st.sidebar:
    st.header("🔧 System Status")
    
    api_key = check_api_key()
    st.success("✅ API Key: OK" if api_key else "❌ API Key: Missing")
    st.success("✅ Script Gen: OK" if SCRIPT_OK else f"❌ Script Gen: {script_error if not SCRIPT_OK else ''}")
    st.success("✅ TTS: OK" if TTS_OK else f"⚠️ TTS: {tts_error if not TTS_OK else ''}")
    
    st.divider()
    st.header("📝 Configure")
    
    topic = st.text_input("Topic", "The Future of AI")
    duration = st.slider("Duration (min)", 1, 10, 3)
    style = st.selectbox("Style", ["Informative", "Conversational", "Educational"])
    
    st.divider()
    st.header("🚀 Generate")
    
    if st.button("Generate Script", type="primary", use_container_width=True):
        if not topic:
            st.error("Enter a topic!")
        elif not SCRIPT_OK:
            st.error("Script generator not available!")
        elif not api_key:
            st.error("API key missing!")
        else:
            with st.spinner("Generating..."):
                try:
                    gen = ScriptGenerator(api_key=api_key)
                    result = gen.generate_script(topic, duration, style)
                    
                    if result.get("success"):
                        st.session_state.script_data = result
                        st.success("✅ Generated!")
                        st.rerun()
                    else:
                        st.error(f"Failed: {result.get('error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📄 Generated Script")
    
    if st.session_state.script_data:
        data = st.session_state.script_data
        
        if "title" in data:
            st.markdown(f"### {data['title']}")
        
        if "description" in data:
            st.info(data['description'])
        
        if "script" in data:
            st.text_area("Script", data["script"], height=400)
    else:
        st.info("👈 Configure and generate a script")

with col2:
    st.subheader("🎵 Audio")
    
    if st.session_state.script_data:
        if st.button("🎤 Generate Audio", type="primary", use_container_width=True):
            if not TTS_OK:
                st.error("TTS not available")
            else:
                try:
                    with st.spinner("Generating audio..."):
                        tts = MockTTSEngine()
                        Path("outputs").mkdir(exist_ok=True)
                        
                        segments = st.session_state.script_data.get('segments', [])
                        text = "\n\n".join([s.get('text', '') for s in segments])
                        
                        audio_file = tts.synthesize(text, "outputs/podcast.wav")
                        st.session_state.audio_path = audio_file
                        st.success("✅ Audio ready!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Audio failed: {str(e)}")
        
        if st.session_state.audio_path and Path(st.session_state.audio_path).exists():
            with open(st.session_state.audio_path, "rb") as f:
                st.audio(f.read())
                
            with open(st.session_state.audio_path, "rb") as f:
                st.download_button("⬇️ Download", f.read(), "podcast.wav", "audio/wav")
    else:
        st.info("Generate a script first")

st.divider()
st.caption("Built with ❤️ using Streamlit and Google Gemini AI")
