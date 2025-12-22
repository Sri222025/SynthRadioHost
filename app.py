"""
Synthetic Radio Host - Streamlit Application
Generate conversational Hinglish podcasts from Wikipedia
"""

import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.wikipedia_fetcher import WikipediaFetcher
from src.script_generator import ScriptGenerator
from src.tts_engine import TTSEngine
from src.audio_processor import AudioProcessor
from src.personas import SPEAKER_PERSONAS, TONE_MODIFIERS
from src.utils import (
    generate_output_filename,
    format_duration,
    save_script_to_file,
    estimate_audio_duration
)

# Page configuration
st.set_page_config(
    page_title="🎙️ Synthetic Radio Host",
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
        color: #FF4B4B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF3333;
    }
    .persona-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = None
if 'generated_audio_path' not in st.session_state:
    st.session_state.generated_audio_path = None
if 'generation_metadata' not in st.session_state:
    st.session_state.generation_metadata = {}
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Header
st.markdown('<div class="main-header">🎙️ The Synthetic Radio Host</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate conversational Hinglish podcasts from Wikipedia topics</div>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # TTS Engine Selection
    tts_engine = st.selectbox(
        "🎤 TTS Engine",
        options=["bark", "elevenlabs"],
        index=0,
        help="Bark is free and supports conversational elements. ElevenLabs needs API key but has better quality."
    )
    
    # API Key inputs (collapsible)
    with st.expander("🔑 API Keys", expanded=False):
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=Config.GEMINI_API_KEY,
            help="Required for script generation"
        )
        
        if tts_engine == "elevenlabs":
            elevenlabs_key = st.text_input(
                "ElevenLabs API Key",
                type="password",
                value=Config.ELEVENLABS_API_KEY,
                help="Required for ElevenLabs TTS"
            )
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        **How it works:**
        1. Select a Wikipedia topic
        2. Choose tone and audience
        3. AI generates Hinglish conversation
        4. TTS converts to natural audio
        
        **Features:**
        - Natural Hinglish code-mixing
        - Age-appropriate personas
        - Conversational elements (laughs, umm, pauses)
        - 2-minute engaging podcasts
        """)
    
    # Credits
    st.markdown("---")
    st.caption("Built for Hackathon 2025")
    st.caption("Powered by: Gemini, Bark/ElevenLabs")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📖 Step 1: Select Topic")
    
    # Search Wikipedia
    search_query = st.text_input(
        "Search Wikipedia",
        placeholder="e.g., ChatGPT, Virat Kohli, ISRO, Taj Mahal...",
        help="Enter any topic to search Wikipedia"
    )
    
    col_search, col_suggest = st.columns([1, 3])
    
    with col_search:
        search_button = st.button("🔍 Search", use_container_width=True)
    
    with col_suggest:
        st.caption("💡 Suggestions: ChatGPT, Virat Kohli, Indian Space Program, Taj Mahal, Bollywood")
    
    # Search results
    if search_button and search_query:
        with st.spinner("Searching Wikipedia..."):
            fetcher = WikipediaFetcher()
            results = fetcher.search_topics(search_query, limit=5)
            st.session_state.search_results = results
    
    # Display search results
    if st.session_state.search_results:
        st.subheader("Search Results:")
        selected_topic = st.radio(
            "Select a topic:",
            options=st.session_state.search_results,
            index=0,
            help="Choose the topic for your podcast"
        )
    else:
        selected_topic = search_query if search_query else "ChatGPT"
        st.info(f"📌 Current topic: **{selected_topic}**")
    
    st.markdown("---")
    
    # Tone and Audience selection
    st.header("🎭 Step 2: Customize Conversation")
    
    col_tone, col_audience = st.columns(2)
    
    with col_tone:
        tone = st.selectbox(
            "🎨 Tone",
            options=["funny", "witty", "professional", "educational", "casual"],
            index=0,
            help="Choose the conversation style"
        )
        
        # Show tone description
        tone_descriptions = {
            "funny": "😄 Humorous and entertaining",
            "witty": "🧠 Smart and clever",
            "professional": "💼 Formal and balanced",
            "educational": "📚 Informative and clear",
            "casual": "😊 Relaxed and friendly"
        }
        st.caption(tone_descriptions[tone])
    
    with col_audience:
        audience = st.selectbox(
            "👥 Target Audience",
            options=["kids", "teenagers", "adults", "elders"],
            index=0,
            help="Choose who the podcast is for"
        )
        
        # Show audience description
        audience_descriptions = {
            "kids": "👦👧 8-12 years (Simple & Fun)",
            "teenagers": "🧑‍🎓 13-19 years (Trendy & Energetic)",
            "adults": "👔 20-50 years (Professional)",
            "elders": "👴👵 50+ years (Respectful & Wise)"
        }
        st.caption(audience_descriptions[audience])

with col2:
    st.header("🎤 Speakers Preview")
    
    # Show persona information
    male_persona = SPEAKER_PERSONAS[audience]["male"]
    female_persona = SPEAKER_PERSONAS[audience]["female"]
    
    st.markdown(f"""
    <div class="persona-box">
        <h4>👤 {male_persona['display_name']}</h4>
        <p><strong>Voice:</strong> {male_persona['voice_characteristics']}</p>
        <p><strong>Style:</strong> {male_persona['speech_pattern']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="persona-box">
        <h4>👤 {female_persona['display_name']}</h4>
        <p><strong>Voice:</strong> {female_persona['voice_characteristics']}</p>
        <p><strong>Style:</strong> {female_persona['speech_pattern']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tone modifier preview
    tone_modifier = TONE_MODIFIERS.get(tone, {}).get(audience, "")
    if tone_modifier:
        st.markdown(f"""
        <div class="info-box">
            <strong>💡 Conversation Style:</strong><br>
            {tone_modifier}
        </div>
        """, unsafe_allow_html=True)

# Generation section
st.markdown("---")
st.header("🎬 Step 3: Generate Podcast")

col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])

with col_gen1:
    generate_button = st.button("🎙️ Generate Radio Episode", use_container_width=True, type="primary")

with col_gen2:
    estimated_time = st.empty()
    estimated_time.info("⏱️ ~2-3 min")

with col_gen3:
    if st.session_state.generated_audio_path:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.generated_script = None
            st.session_state.generated_audio_path = None
            st.rerun()

# Generation process
if generate_button:
    if not gemini_key and not Config.GEMINI_API_KEY:
        st.error("❌ Please provide Gemini API Key in the sidebar!")
    else:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch Wikipedia article
            status_text.text("📖 Fetching Wikipedia article...")
            progress_bar.progress(10)
            
            fetcher = WikipediaFetcher()
            article = fetcher.get_article_for_script(selected_topic)
            
            if not article:
                st.error(f"❌ Could not fetch Wikipedia article for '{selected_topic}'")
                st.stop()
            
            progress_bar.progress(20)
            
            # Step 2: Generate script
            status_text.text("✍️ Generating conversational script...")
            progress_bar.progress(30)
            
            generator = ScriptGenerator(api_key=gemini_key or Config.GEMINI_API_KEY)
            
            script_result = generator.generate_script(
                topic=selected_topic,
                tone=tone,
                audience=audience,
                wikipedia_content=article['key_facts']
            )
            
            if not script_result:
                st.error("❌ Failed to generate script. Please try again.")
                st.stop()
            
            st.session_state.generated_script = script_result['script']
            progress_bar.progress(50)
            
            # Step 3: Parse script
            status_text.text("🎭 Parsing dialogue segments...")
            segments = generator.parse_script_by_speaker(script_result['script'], audience)
            
            if not segments:
                st.error("❌ Failed to parse script. Please regenerate.")
                st.stop()
            
            progress_bar.progress(60)
            
            # Step 4: Generate audio (TTS)
            status_text.text(f"🎤 Generating audio with {tts_engine.upper()}... (this may take 1-2 min)")
            progress_bar.progress(70)
            
            # Initialize TTS engine
            try:
                tts = TTSEngine(engine=tts_engine)
            except Exception as e:
                st.error(f"❌ TTS Engine initialization failed: {str(e)}")
                st.info("💡 Tip: If using Bark, it needs to download models on first run (~2GB)")
                st.stop()
            
            # Generate audio for each segment
            temp_dir = Config.TEMP_DIR / f"generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            audio_files = tts.generate_full_conversation(
                segments=segments,
                audience=audience,
                output_dir=temp_dir
            )
            
            if not audio_files:
                st.error("❌ Failed to generate audio files.")
                st.stop()
            
            progress_bar.progress(85)
            
            # Step 5: Merge audio
            status_text.text("🎵 Merging audio segments...")
            
            processor = AudioProcessor()
            output_filename = generate_output_filename(selected_topic, audience, tone)
            output_path = Config.SAMPLES_DIR / output_filename
            
            success = processor.process_conversation(
                audio_files=audio_files,
                output_path=output_path,
                pause_duration=500  # 0.5 second pause between speakers
            )
            
            if not success:
                st.error("❌ Failed to merge audio files.")
                st.stop()
            
            progress_bar.progress(95)
            
            # Step 6: Save script
            status_text.text("💾 Saving script...")
            script_filename = output_filename.replace('.mp3', '.txt')
            script_path = Config.SAMPLES_DIR / "scripts" / script_filename
            save_script_to_file(script_result['script'], script_path)
            
            # Store in session state
            st.session_state.generated_audio_path = output_path
            st.session_state.generation_metadata = {
                'topic': selected_topic,
                'tone': tone,
                'audience': audience,
                'word_count': script_result['word_count'],
                'duration': processor.get_audio_duration(output_path),
                'script_path': str(script_path),
                'audio_path': str(output_path),
                'tts_engine': tts_engine,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            progress_bar.progress(100)
            status_text.text("✅ Generation complete!")
            
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during generation: {str(e)}")
            st.exception(e)

# Display results
if st.session_state.generated_audio_path and st.session_state.generated_script:
    st.markdown("---")
    st.header("✅ Generated Podcast")
    
    metadata = st.session_state.generation_metadata
    
    # Success message
    st.markdown(f"""
    <div class="success-box">
        <h3>🎉 Your podcast is ready!</h3>
        <p><strong>Topic:</strong> {metadata.get('topic', 'N/A')}</p>
        <p><strong>Audience:</strong> {metadata.get('audience', 'N/A').title()} | 
           <strong>Tone:</strong> {metadata.get('tone', 'N/A').title()}</p>
        <p><strong>Duration:</strong> {format_duration(metadata.get('duration', 0))} | 
           <strong>Words:</strong> {metadata.get('word_count', 0)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio player
    st.subheader("🔊 Listen to Your Podcast")
    
    if Path(st.session_state.generated_audio_path).exists():
        audio_file = open(st.session_state.generated_audio_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
        audio_file.close()
        
        # Download button
        with open(st.session_state.generated_audio_path, 'rb') as f:
            st.download_button(
                label="💾 Download MP3",
                data=f.read(),
                file_name=Path(st.session_state.generated_audio_path).name,
                mime="audio/mp3",
                use_container_width=True
            )
    else:
        st.error("Audio file not found!")
    
    # Script display
    st.subheader("📜 Generated Script")
    
    with st.expander("View Full Script", expanded=False):
        st.text_area(
            "Script Content",
            value=st.session_state.generated_script,
            height=400,
            disabled=True
        )
        
        # Download script
        st.download_button(
            label="📄 Download Script",
            data=st.session_state.generated_script,
            file_name=f"script_{metadata.get('topic', 'podcast')}_{metadata.get('audience')}_{metadata.get('tone')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    # Metadata
    with st.expander("ℹ️ Generation Details", expanded=False):
        st.json(metadata)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>🎙️ <strong>Synthetic Radio Host</strong> | Built with ❤️ using Streamlit, Gemini, and Bark</p>
    <p>Create engaging Hinglish podcasts from any Wikipedia topic!</p>
</div>
""", unsafe_allow_html=True)
