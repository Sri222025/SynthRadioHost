"""
Unit tests for TTS Engine
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.tts_engine import TTSEngine

class TestTTSEngineInit:
    """Test TTS Engine initialization"""
    
    @patch('src.tts_engine.TTSEngine._init_bark')
    def test_init_bark(self, mock_init_bark):
        """Test initialization with Bark engine"""
        engine = TTSEngine(engine="bark")
        
        assert engine.engine == "bark"
        mock_init_bark.assert_called_once()
    
    @patch('src.tts_engine.TTSEngine._init_elevenlabs')
    def test_init_elevenlabs(self, mock_init_elevenlabs):
        """Test initialization with ElevenLabs engine"""
        engine = TTSEngine(engine="elevenlabs")
        
        assert engine.engine == "elevenlabs"
        mock_init_elevenlabs.assert_called_once()
    
    def test_init_invalid_engine(self):
        """Test initialization with invalid engine raises error"""
        with pytest.raises(ValueError, match="Unsupported TTS engine"):
            TTSEngine(engine="invalid_engine")


class TestBarkTTS:
    """Test Bark TTS functionality"""
    
    @patch('src.tts_engine.preload_models')
    @patch('src.tts_engine.generate_audio')
    @patch('src.tts_engine.SAMPLE_RATE', 24000)
    def test_generate_speech_bark_success(self, mock_generate, mock_preload, temp_test_dir):
        """Test successful Bark speech generation"""
        import numpy as np
        
        # Mock audio generation
        mock_audio = np.random.randn(24000)  # 1 second of audio
        mock_generate.return_value = mock_audio
        
        engine = TTSEngine(engine="bark")
        output_path = temp_test_dir / "test_bark.wav"
        
        success = engine.generate_speech_bark(
            text="Hello world",
            voice_preset="v2/en_speaker_6",
            output_path=output_path
        )
        
        assert success
        mock_generate.assert_called_once()
    
    @patch('src.tts_engine.preload_models')
    @patch('src.tts_engine.generate_audio')
    @patch('src.tts_engine.SAMPLE_RATE', 24000)
    def test_generate_speech_bark_error(self, mock_generate, mock_preload, temp_test_dir):
        """Test Bark generation error handling"""
        mock_generate.side_effect = Exception("Generation failed")
        
        engine = TTSEngine(engine="bark")
        output_path = temp_test_dir / "test_bark.wav"
        
        success = engine.generate_speech_bark(
            text="Hello world",
            voice_preset="v2/en_speaker_6",
            output_path=output_path
        )
        
        assert not success


class TestElevenLabsTTS:
    """Test ElevenLabs TTS functionality"""
    
    @patch('src.tts_engine.set_api_key')
    @patch('src.tts_engine.generate')
    @patch('src.tts_engine.voices')
    @patch.object(Config, 'ELEVENLABS_API_KEY', 'test_key')
    def test_generate_speech_elevenlabs_success(self, mock_voices, mock_generate, mock_set_key, temp_test_dir):
        """Test successful ElevenLabs speech generation"""
        mock_audio_data = b"fake_audio_data"
        mock_generate.return_value = mock_audio_data
        
        engine = TTSEngine(engine="elevenlabs")
        output_path = temp_test_dir / "test_elevenlabs.mp3"
        
        success = engine.generate_speech_elevenlabs(
            text="Hello world",
            voice_name="adam",
            output_path=output_path
        )
        
        assert success
        assert output_path.exists()


class TestDialogueGeneration:
    """Test dialogue segment generation"""
    
    @patch('src.tts_engine.preload_models')
    @patch('src.tts_engine.generate_audio')
    @patch('src.tts_engine.SAMPLE_RATE', 24000)
    def test_generate_dialogue_segment(self, mock_generate, mock_preload, temp_test_dir):
        """Test generating a single dialogue segment"""
        import numpy as np
        
        mock_audio = np.random.randn(24000)
        mock_generate.return_value = mock_audio
        
        engine = TTSEngine(engine="bark")
        output_path = temp_test_dir / "segment.wav"
        
        success = engine.generate_dialogue_segment(
            dialogue="Arey yaar, hello! [excited]",
            speaker="male",
            audience="kids",
            output_path=output_path
        )
        
        assert success
    
    @patch('src.tts_engine.preload_models')
    @patch('src.tts_engine.generate_audio')
    @patch('src.tts_engine.SAMPLE_RATE', 24000)
    def test_generate_full_conversation(self, mock_generate, mock_preload, sample_segments_kids, temp_test_dir):
        """Test generating full conversation from segments"""
        import numpy as np
        
        mock_audio = np.random.randn(24000)
        mock_generate.return_value = mock_audio
        
        engine = TTSEngine(engine="bark")
        
        audio_files = engine.generate_full_conversation(
            segments=sample_segments_kids,
            audience="kids",
            output_dir=temp_test_dir
        )
        
        assert len(audio_files) == len(sample_segments_kids)
        assert all(Path(f).exists() for f in audio_files)
