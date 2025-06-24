# TranscribeMe 📞➡️📝

**A phone-based transcription service that converts voice calls to formatted text and delivers results via SMS.**

## 🎯 What is TranscribeMe?

TranscribeMe is a service that provides a dedicated phone number for voice-to-text transcription. Users call the number, speak their message, and receive a professionally formatted transcript via SMS with a hosted link to the full text.

### 🔄 How it Works

1. **📞 Call the Service**: Users dial the TranscribeMe phone number from their mobile device
2. **🔍 Caller Identification**: System recognizes and validates the caller's mobile number
3. **🎤 Voice Recording**: User speaks their message (meeting notes, ideas, reminders, etc.)
4. **🤖 AI Transcription**: Advanced speech-to-text converts audio to accurate text
5. **✨ Smart Formatting**: AI rewrites and formats the transcript for clarity and structure
6. **📱 SMS Delivery**: Formatted transcript is hosted online and link sent via SMS
7. **🔗 Access Anywhere**: User clicks link to view, copy, or share the formatted text

### ✅ Key Features

- **📱 Mobile-Only Access**: Service only accepts calls from recognized mobile numbers
- **🔒 Secure & Private**: Each transcript is privately hosted with unique access links
- **🎯 Smart Formatting**: AI enhances raw transcripts for better readability
- **⚡ Fast Delivery**: SMS notifications sent within seconds of call completion
- **📧 Multiple Formats**: Output optimized for emails, documents, or notes
- **🌐 Web Access**: Hosted transcripts accessible from any device

### 🎯 Use Cases

- **📝 Meeting Notes**: Record and format meeting discussions on-the-go
- **💡 Idea Capture**: Quickly capture and organize creative thoughts
- **📧 Email Drafting**: Speak emails and receive formatted drafts
- **📋 Task Lists**: Convert spoken to-dos into organized lists
- **📚 Interview Transcripts**: Professional formatting for interviews
- **🚗 Hands-Free Documentation**: Safe voice recording while driving

## 🏗️ Technical Architecture

### Core Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Phone System  │    │  Transcription   │    │   SMS Gateway   │
│                 │    │     Engine       │    │                 │
│ • Call Handling │───▶│ • Speech-to-Text │───▶│ • Link Hosting  │
│ • Number Verify │    │ • AI Formatting  │    │ • SMS Delivery  │
│ • Audio Record  │    │ • Text Storage   │    │ • Mobile Verify │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Technology Stack

- **📞 Telephony**: Twilio Voice API for call handling
- **🎤 Speech Recognition**: OpenAI Whisper or Google Speech-to-Text
- **🤖 AI Formatting**: OpenAI GPT for text enhancement and structuring
- **📱 SMS Gateway**: Twilio SMS API for message delivery
- **🌐 Web Hosting**: Fast CDN for transcript hosting
- **🔐 Security**: Encrypted storage and secure access links

## 🚀 Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

### Prerequisites

- Python 3.11+
- uv (install from https://docs.astral.sh/uv/getting-started/installation/)
- Twilio Account (for phone/SMS services)
- OpenAI API Key (for transcription and formatting)
- Flask or FastAPI (for web server)

### Installation

```bash
# Clone the repository
git clone git@github.com:alexdong/TranscribeMe.git
cd TranscribeMe

# Install dependencies
make install
# or
uv sync --dev

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Service Configuration
BASE_URL=https://your-domain.com
DATABASE_URL=your_database_connection_string
```

### Development Commands

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint

# Run all checks
make check

# Start development server
make dev

# Clean up
make clean
```

## 📋 API Endpoints

### Webhook Endpoints (Twilio)

- `POST /webhook/voice` - Handle incoming voice calls
- `POST /webhook/sms` - Handle SMS responses (optional)

### Public Endpoints

- `GET /transcript/{id}` - View hosted transcript
- `GET /health` - Service health check

## 🔧 Configuration

### Call Flow Configuration

```python
# Example configuration for different transcript formats
TRANSCRIPT_FORMATS = {
    "email": {
        "prompt": "Format this as a professional email draft",
        "structure": "subject_body"
    },
    "notes": {
        "prompt": "Organize this into clear bullet points",
        "structure": "bulleted_list"
    },
    "meeting": {
        "prompt": "Format as meeting minutes with action items",
        "structure": "structured_minutes"
    }
}
```

### Security Settings

```python
# Mobile number validation
ALLOWED_COUNTRY_CODES = ["+1", "+44", "+61"]  # US, UK, Australia
MAX_CALL_DURATION = 300  # 5 minutes
TRANSCRIPT_EXPIRY = 7  # days
```

## 🧪 Testing

```bash
# Run all tests
make test

# Test specific components
uv run pytest tests/test_transcription.py
uv run pytest tests/test_sms_gateway.py
uv run pytest tests/test_phone_handler.py

# Integration tests
uv run pytest tests/integration/
```

## 📦 Deployment

### Docker Deployment

```bash
# Build container
docker build -t transcribeme .

# Run with environment variables
docker run -d \
  --env-file .env \
  -p 8000:8000 \
  transcribeme
```

### Cloud Deployment

The service is designed to run on cloud platforms with webhook support:

- **Heroku**: Easy deployment with Twilio webhooks
- **AWS Lambda**: Serverless deployment option
- **Google Cloud Run**: Container-based deployment
- **Railway/Render**: Simple deployment platforms

## 🔒 Privacy & Security

- **🔐 Encrypted Storage**: All audio and transcripts encrypted at rest
- **⏰ Auto-Expiry**: Transcripts automatically deleted after 7 days
- **🔗 Secure Links**: Unique, non-guessable URLs for transcript access
- **📱 Mobile Verification**: Only registered mobile numbers can access service
- **🚫 No Audio Retention**: Audio files deleted immediately after transcription

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@transcribeme.com
- 📖 Documentation: [docs.transcribeme.com](https://docs.transcribeme.com)
- 🐛 Issues: [GitHub Issues](https://github.com/alexdong/TranscribeMe/issues)

---

**Made with ❤️ for seamless voice-to-text transcription**
