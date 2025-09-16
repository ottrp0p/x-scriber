import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import openai
from django.conf import settings


class WhisperTranscriber:
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )

            return {
                "text": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": transcript.segments if hasattr(transcript, 'segments') else []
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    def save_transcription(self, transcription: Dict[str, Any], output_path: str) -> bool:
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Failed to save transcription: {str(e)}")
            return False

    def transcribe_and_save(self, audio_file_path: str, output_path: str, language: Optional[str] = None) -> bool:
        try:
            transcription = self.transcribe(audio_file_path, language)
            return self.save_transcription(transcription, output_path)
        except Exception as e:
            print(f"Transcribe and save failed: {str(e)}")
            return False