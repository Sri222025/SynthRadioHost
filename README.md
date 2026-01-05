cat > README.md << 'EOF'
# 🎙️ Samaahar — Knowledge Spoken in Hinglish

> AI-Powered Podcast Generator | Wikipedia to Hinglish Audio

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)](https://groq.com)
[![Edge TTS](https://img.shields.io/badge/Microsoft-Edge%20TTS-00A4EF?logo=microsoft&logoColor=white)](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/)

---

## 📖 Overview

**Samaahar** transforms Wikipedia articles into engaging 2-person Hinglish podcasts, tailored for different age groups (Kids, Teenagers, Adults, Elderly). Search any topic, select your audience, and get a natural-sounding MP3 podcast in under 3 minutes!

### 🎯 Key Features

- 🌐 **Wikipedia Integration** - Search and select from 10M+ articles
- 🎭 **4 Audience Profiles** - Age-adaptive content and voice characteristics
- 🗣️ **Natural Hinglish** - 60% Hindi, 40% English conversational style
- 🎤 **2-Speaker Format** - Rajesh & Priya (Indian English voices)
- 📱 **Mobile-First UI** - Jio-inspired design for Indian users
- ⚡ **Fast Generation** - 2.5 min average (script + audio)

---

## 🚀 Live Demo

**Try it now:** https://synthradiohost1.streamlit.app/

**Watch our pitch:** https://teams.microsoft.com/l/meetingrecap?driveId=b%21GSFvoZRT0UCzFNA4fL4Otash8U047rhHuuMGNVIc-PWt5X6LkD-_QZGXC3qUPgQ3&driveItemId=01HROUNA6X53HWQXSFFFAIRG3ZKECVQLKQ&sitePath=https%3A%2F%2Frilcloud-my.sharepoint.com%2F%3Av%3A%2Fg%2Fpersonal%2Fsridevi_nune_ril_com%2FIQDX7s9oXkUpQIibeVEFWC1QAVHeHn7y9pBZBwGNwSqdQ-g&fileUrl=https%3A%2F%2Frilcloud-my.sharepoint.com%2Fpersonal%2Fsridevi_nune_ril_com%2FDocuments%2FRecordings%2FMeeting%2520with%2520Sridevi%2520Nune-20260105_111147-Meeting%2520Recording.mp4%3Fweb%3D1&threadId=19%3Ameeting_NDQ4NjAxOTEtMjJlMi00NjJjLWFjMTAtMWJiN2I0YTk3MmE2%40thread.v2&organizerId=40c7a15d-2218-40fb-9608-842ee0757dbc&tenantId=fe1d95a9-4ce1-41a5-8eab-6dd43aa26d9f&callId=83281106-eec9-417f-b629-90371920e835&threadType=Meeting&meetingType=MeetNow&subType=RecapSharingLink_RecapCore

---

## 🏗️ Tech Stack

| Component | Technology | Why? |
|-----------|------------|------|
| **Frontend** | Streamlit | Rapid prototyping, Python-native |
| **AI Script** | Groq (Llama 3.3 70B) | 130 tok/s speed, free tier |
| **TTS** | Microsoft Edge TTS | Indian voices, free, high quality |
| **Data** | Wikipedia API | 10M+ articles, reliable |

---

## 📦 Installation

### Prerequisites

- Python 3.11 (⚠️ NOT 3.13 - pydub incompatibility)
- Groq API Key (shared in secrets in streamlit for security)

### Local Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/samaahar-podcast-generator.git
cd samaahar-podcast-generator

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml and add your GROQ_API_KEY

# Run app
streamlit run app.py
