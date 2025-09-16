# API Interface Contracts

## OpenAI Whisper API

### Transcription Endpoint
- **URL**: `https://api.openai.com/v1/audio/transcriptions`
- **Method**: POST
- **Content-Type**: multipart/form-data

#### Required Parameters:
- `file`: Audio file (flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm)
- `model`: Model to use (e.g., "whisper-1")

#### Optional Parameters:
- `language`: ISO-639-1 language code
- `prompt`: Text to guide the model's style
- `response_format`: json, text, srt, verbose_json, or vtt (default: json)
- `temperature`: 0 to 1 (default: 0)

#### Response Format (JSON):
```json
{
  "text": "Transcribed text here"
}
```

#### Response Format (Verbose JSON):
```json
{
  "task": "transcribe",
  "language": "english",
  "duration": 8.470000267028809,
  "text": "Transcribed text here",
  "segments": [
    {
      "id": 0,
      "seek": 0,
      "start": 0.0,
      "end": 4.0,
      "text": " Transcribed text here",
      "tokens": [50364, 1396, 264, 2316, 294, 264, 1504, 13, 50564],
      "temperature": 0.0,
      "avg_logprob": -0.6674491882324218,
      "compression_ratio": 1.2363636363636363,
      "no_speech_prob": 0.022097285091876984
    }
  ]
}
```

## OpenAI Chat Completions API

### Chat Completions Endpoint
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Method**: POST
- **Content-Type**: application/json

#### Required Parameters:
- `model`: Model to use (e.g., "gpt-3.5-turbo", "gpt-4")
- `messages`: Array of message objects

#### Message Object Format:
```json
{
  "role": "system|user|assistant",
  "content": "Message content"
}
```

#### Optional Parameters:
- `temperature`: 0 to 2 (default: 1)
- `max_tokens`: Maximum tokens to generate
- `top_p`: 0 to 1 (default: 1)
- `frequency_penalty`: -2.0 to 2.0 (default: 0)
- `presence_penalty`: -2.0 to 2.0 (default: 0)
- `stop`: Up to 4 sequences where API will stop generating

#### Response Format:
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response content here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

## Internal Component Interfaces

### WhisperTranscriber Class
```python
class WhisperTranscriber:
    def __init__(self, api_key: str, model: str = "whisper-1")
    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> dict
    def save_transcription(self, transcription: dict, output_path: str) -> bool
```

### ChatCompletionProcessor Class
```python
class ChatCompletionProcessor:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo")
    def process_transcription_to_trd(self, transcription: str, existing_trd: str = "") -> str
    def parse_trd_ontology(self, trd_content: str) -> dict
    def update_trd_sections(self, ontology: dict, new_content: str) -> dict
    def generate_trd_document(self, ontology: dict) -> str
```

### RecordingHandler Class
```python
class RecordingHandler:
    def __init__(self, chunk_duration: int = 30, output_dir: str = "data/audio-recordings")
    def start_recording(self, project_id: str) -> bool
    def stop_recording(self) -> bool
    def get_audio_chunks(self, project_id: str) -> List[str]
```

### ProjectHandler Class
```python
class ProjectHandler:
    def __init__(self, data_dir: str = "data")
    def create_project(self, name: str, description: str) -> str
    def get_project_id(self, name: str) -> Optional[str]
    def orchestrate_processing(self, project_id: str, audio_file: str) -> bool
```

## File Naming Conventions

### Audio Recordings
- Format: `{project_id}_audiochunk_{i}.wav`
- Location: `data/audio-recordings/`

### Transcriptions
- Format: `{project_id}_transcription_{i}.json`
- Location: `data/raw-transcriptions/`

### TRD Documents
- Format: `{project_id}_trd.md`
- Location: `data/output/`

### Project Metadata
- Format: `{project_id}_metadata.json`
- Location: `data/project_metadata/`