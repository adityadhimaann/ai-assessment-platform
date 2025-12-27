# Lisa - AI Assessment Platform

An intelligent assessment platform with adaptive difficulty, AI-powered evaluation, and custom voice feedback featuring Lisa, your AI assessment assistant.

## Features

- 🤖 **AI-Powered Evaluation**: Lisa uses OpenAI GPT-4o for intelligent answer assessment
- 🎯 **Adaptive Difficulty**: Automatically adjusts question difficulty based on performance
- 🎤 **Custom Voice Feedback**: Lisa speaks with a custom ElevenLabs voice
- 🎙️ **Speech Recognition**: Voice input for answers (browser-based)
- 📊 **Real-time Progress Tracking**: Visual question sidebar with status indicators
- 🔄 **Session Management**: Persistent assessment sessions
- 🎨 **Modern UI**: React + TypeScript + Tailwind CSS

## Meet Lisa

Lisa is your AI assessment assistant who:
- Generates personalized questions based on your topic
- Evaluates your answers with detailed feedback
- Adapts difficulty to match your skill level
- Provides encouraging voice feedback with a custom voice

## Tech Stack

### Backend (aibackend/)
- **Framework**: FastAPI (Python)
- **AI Services**: 
  - OpenAI GPT-4o (evaluation & question generation)
  - OpenAI Whisper (audio transcription)
  - ElevenLabs (text-to-speech)
- **Testing**: pytest with property-based testing (Hypothesis)
- **Code Coverage**: 91%+

### Frontend (aifrontend/)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Query
- **Routing**: React Router

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- ElevenLabs API key (with custom voice)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ai-insight-hub
   ```

2. **Backend Setup**
   ```bash
   cd aibackend
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Frontend Setup**
   ```bash
   cd aifrontend
   
   # Install dependencies
   npm install
   
   # Configure environment
   cp .env.example .env
   # Edit .env if needed (default: http://localhost:8000/api)
   ```

### Running the Application

**Option 1: Use the startup script**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Option 2: Start services manually**

Terminal 1 (Backend):
```bash
cd aibackend
python3 main.py
```

Terminal 2 (Frontend):
```bash
cd aifrontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Configuration

### Backend Environment Variables

Create `aibackend/.env` with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# ElevenLabs Configuration
TTS_API_KEY=your_elevenlabs_api_key
TTS_SERVICE=elevenlabs
ELEVENLABS_VOICE_ID=your_custom_voice_id
ELEVENLABS_MODEL_ID=eleven_turbo_v2

# Development Mode (uses mock responses)
DEV_MODE=false

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Getting Your Lisa Voice ID

1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app/voice-lab)
2. Find your custom voice for Lisa
3. Click the three dots (...) → "Copy voice ID"
4. Paste into `ELEVENLABS_VOICE_ID` in `.env`

See `GET_VOICE_ID.md` for detailed instructions.

## Testing

### Backend Tests
```bash
cd aibackend
pytest                          # Run all tests
pytest --cov                    # With coverage
pytest -v                       # Verbose output
```

### Test Voice Configuration
```bash
cd aibackend
python3 test_devi_voice.py
```

## Project Structure

```
ai-insight-hub/
├── aibackend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── clients/       # External API clients
│   │   ├── models.py      # Pydantic models
│   │   └── exceptions.py  # Custom exceptions
│   ├── config/            # Configuration
│   ├── tests/             # Test suite
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
│
├── aifrontend/            # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utilities & API client
│   │   └── pages/         # Page components
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
│
├── .kiro/                 # Kiro AI specs
├── start-dev.sh           # Development startup script
└── README.md              # This file
```

## API Endpoints

### Assessment
- `POST /api/start-session` - Start new assessment session
- `GET /api/get-next-question` - Get next question
- `POST /api/submit-answer` - Submit answer for evaluation

### Audio
- `POST /api/transcribe-audio` - Transcribe audio to text
- `POST /api/generate-voice-feedback` - Generate TTS audio

See full API documentation at http://localhost:8000/docs

## Development Mode

Set `DEV_MODE=true` in `aibackend/.env` to:
- Use mock AI responses (no API costs)
- Test without consuming API credits
- Faster development iteration

## Documentation

- `SETUP_COMPLETE.md` - Complete setup guide
- `ELEVENLABS_VOICE_SETUP.md` - Voice configuration details
- `GET_VOICE_ID.md` - How to get your voice ID
- `INTEGRATION_GUIDE.md` - Frontend-backend integration
- `VOICE_INTEGRATION_SUMMARY.md` - TTS implementation details

## Features in Detail

### Adaptive Difficulty
- Automatically adjusts based on performance
- Tracks consecutive high/low scores
- Smooth difficulty transitions

### AI Evaluation
- GPT-4o powered answer assessment
- Detailed feedback generation
- Score calculation (0-100)
- Correctness determination

### Voice Feedback
- Custom ElevenLabs voice (Lisa)
- Natural, engaging feedback
- Fallback to browser TTS
- Automatic audio playback

### Session Management
- Persistent session state
- Performance tracking
- Question history
- Progress visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions:
- Check the documentation files
- Review API docs at /docs endpoint
- Check backend logs for errors

## Acknowledgments

- OpenAI for GPT-4o and Whisper APIs
- ElevenLabs for TTS services
- shadcn/ui for UI components
# ai-assessment-platform
