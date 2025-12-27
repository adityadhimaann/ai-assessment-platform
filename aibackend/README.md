# AI Assessment Backend

FastAPI-based backend for intelligent educational assessment with adaptive difficulty.

## Features

- 🤖 AI-powered answer evaluation using GPT-4o
- 📈 Adaptive difficulty based on student performance
- 🎤 Audio transcription with Whisper API
- 🔊 Voice feedback generation with TTS
- 📊 Session management and performance tracking

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- `POST /start-session` - Start a new assessment session
- `GET /get-next-question` - Get the next question for a session
- `POST /submit-answer` - Submit an answer for evaluation
- `POST /transcribe-audio` - Transcribe audio to text
- `POST /generate-voice-feedback` - Generate voice feedback from text

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── services/       # Business logic
│   ├── routers/        # API endpoints
│   ├── clients/        # External API clients
│   ├── middleware/     # Middleware components
│   └── utils/          # Utility functions
├── config/             # Configuration
├── tests/              # Test suite
├── main.py             # Application entry point
└── requirements.txt    # Dependencies
```

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT
