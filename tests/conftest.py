"""
Pytest configuration and fixtures
"""
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_wikipedia_content():
    """Sample Wikipedia content for testing"""
    return """
    ChatGPT is an artificial intelligence chatbot developed by OpenAI.
    It is built on top of OpenAI's GPT-3 family of large language models.
    ChatGPT was launched in November 2022 and gained widespread attention
    for its detailed responses and articulate answers across many domains.
    The chatbot uses Reinforcement Learning from Human Feedback (RLHF) to
    improve its responses over time.
    """

@pytest.fixture
def sample_script_kids():
    """Sample script for kids audience"""
    return """
BOY: Arey yaar, ChatGPT ke baare mein suna hai? [excited]
GIRL: Haan! Wo toh bahut cool hai! [giggles] Matlab ek robot jo tumse baat karta hai.
BOY: [umm] Robot? Matlab Terminator jaisa?
GIRL: Nahin yaar! [laughs] Wo toh movies mein hota hai. Ye toh computer program hai.
BOY: Achha achha! Toh ye kya kar sakta hai? [curious]
GIRL: Bahut kuch! Homework help kar sakta hai, stories likh sakta hai... [excited]
BOY: Wow! Matlab mujhe padhai mein help karega? [surprised]
GIRL: Haan! But khud se bhi kuch seekhna padega na! [giggles]
"""

@pytest.fixture
def sample_script_teens():
    """Sample script for teenagers audience"""
    return """
TEEN BOY: Bro, ChatGPT is literally the GOAT yaar [confident]
TEEN GIRL: GOAT toh hai, but bro... that temper though! [laughs]
TEEN BOY: [umm] Arre yaar, what temper? It's just an AI!
TEEN GIRL: Haan okay okay... but it's so smart na [excited]
TEEN BOY: Exactly! College assignments ka best friend [witty]
TEEN GIRL: But dependency toh nahi honi chahiye [thoughtful]
"""

@pytest.fixture
def sample_segments_kids():
    """Sample parsed segments for kids"""
    return [
        {
            "speaker": "male",
            "speaker_name": "BOY",
            "dialogue": "Arey yaar, ChatGPT ke baare mein suna hai? [excited]"
        },
        {
            "speaker": "female",
            "speaker_name": "GIRL",
            "dialogue": "Haan! Wo toh bahut cool hai! [giggles]"
        }
    ]

@pytest.fixture
def temp_test_dir(tmp_path):
    """Create temporary test directory"""
    test_dir = tmp_path / "test_outputs"
    test_dir.mkdir(exist_ok=True)
    return test_dir
