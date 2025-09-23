# X-Scriber

Live microphone recording with OpenAI Whisper transcription and automatic Technical Requirements Document (TRD) generation.
<img width="1464" height="744" alt="Screenshot 2025-09-16 at 3 11 43 AM" src="https://github.com/user-attachments/assets/2505b874-3441-4d8b-8564-4188961335c7" />

## Features

- **Live Audio Recording**: Record audio in real-time with automatic chunking
- **AI Transcription**: Uses OpenAI Whisper for accurate speech-to-text conversion
- **TRD Generation**: Automatically generates and updates Technical Requirements Documents using OpenAI Chat Completions
- **Web Interface**: Modern, responsive web interface for project management
- **Project Management**: Organize recordings and documents by project
- **Real-time Updates**: Live updates to transcriptions and documents during recording

## Quick Start

### Prerequisites

- **Python 3.12 or earlier** (Python 3.13+ not supported due to pydub dependency requiring audioop module)
- OpenAI API key with access to Whisper and Chat Completions
- Microphone access permissions

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd x-scriber
```

2. Create virtual environment (with Python 3.12 or earlier):
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. Run Django setup:
```bash
python manage.py migrate
python manage.py collectstatic
```

6. Start the development server:
```bash
python manage.py runserver
```

7. Open your browser and navigate to `http://localhost:8000`

### Configuration

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here
DJANGO_SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

## Usage

### Creating a Project

1. Click "New Project" button
2. Enter project name and description
3. Click "Create Project"

### Recording Audio

1. Select a project from the project list
2. Click "Start Recording" button
3. Speak into your microphone
4. Click "Stop Recording" when finished

### Viewing Results

- **TRD Panel**: View the generated Technical Requirements Document
- **Transcription List**: Browse individual audio chunks
- **Transcription Detail**: View raw transcription text

## Architecture

### Components

- **WhisperTranscriber**: Handles OpenAI Whisper API integration
- **ChatCompletionProcessor**: Manages TRD generation and updates
- **RecordingHandler**: Manages live audio recording and chunking
- **ProjectHandler**: Orchestrates the entire workflow
- **Django Backend**: Provides REST API and web interface
- **Frontend**: Modern JavaScript interface for user interaction

### Data Flow

1. User starts recording for a project
2. Audio is chunked every 30 seconds (configurable)
3. Audio chunks are sent to OpenAI Whisper for transcription
4. Transcriptions are processed by OpenAI Chat Completions to update the TRD
5. Frontend polls for updates and displays results in real-time

## API Endpoints

- `GET /api/projects/` - List all projects
- `POST /api/create_project/` - Create a new project
- `GET /api/projects/{id}/` - Get project details and TRD
- `GET /api/projects/{id}/transcriptions/` - List transcriptions for a project
- `POST /api/recording/start/` - Start recording for a project
- `POST /api/recording/stop/` - Stop current recording

## Development

### Running Tests

```bash
python manage.py test
```

### Project Structure

```
x-scriber/
├── config/                   # Django configuration
├── xscriber/                 # Main Django app
│   ├── modules/              # Core business logic
│   │   ├── transcriber.py    # OpenAI Whisper integration
│   │   ├── chat_completion.py # OpenAI Chat Completions
│   │   ├── recording_handler.py # Audio recording
│   │   └── project_handler.py # Project orchestration
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS assets
│   └── tests/                # Unit tests
├── tests/                    # Integration tests
├── docs/                     # Documentation
│   ├── TODO.md              # Project progress tracking
│   ├── user_todo.md         # User setup requirements
│   └── interface.md         # API interface documentation
├── data/                     # Local data storage
│   ├── project_metadata/     # Project information
│   ├── audio-recordings/     # Audio chunks
│   ├── raw-transcriptions/   # Whisper outputs
│   └── output/               # Generated TRDs
├── CLAUDE.md                 # Claude Code assistant rules
├── README.md                 # This file
└── requirements.txt          # Python dependencies
```

### Adding New Features

1. Write tests first (`xscriber/tests/` or `tests/`)
2. Implement functionality in appropriate module
3. Update Django views if needed
4. Test thoroughly
5. Update documentation

### Documentation

For detailed documentation, see the `docs/` folder:
- [`docs/TODO.md`](docs/TODO.md) - Project progress and task tracking
- [`docs/user_todo.md`](docs/user_todo.md) - User setup requirements and dependencies
- [`docs/interface.md`](docs/interface.md) - API interface contracts and specifications

## Troubleshooting

### Common Issues

1. **Microphone not working**: Check browser permissions
2. **OpenAI API errors**: Verify API key and quota
3. **Audio recording fails**: Check PyAudio installation
4. **TRD not updating**: Check OpenAI Chat Completions quota

### Logs

Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity=2
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please create an issue in the GitHub repository.
