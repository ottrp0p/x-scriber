import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from django.test import TestCase
from xscriber.modules.transcriber import WhisperTranscriber


class WhisperTranscriberTests(TestCase):
    def setUp(self):
        self.transcriber = WhisperTranscriber(api_key="test_api_key")

    def test_init_with_api_key(self):
        transcriber = WhisperTranscriber(api_key="test_key")
        self.assertEqual(transcriber.api_key, "test_key")
        self.assertEqual(transcriber.model, "whisper-1")

    def test_init_without_api_key_raises_error(self):
        with patch('django.conf.settings.OPENAI_API_KEY', None):
            with self.assertRaises(ValueError):
                WhisperTranscriber()

    @patch('xscriber.modules.transcriber.openai.OpenAI')
    def test_transcribe_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Test transcription"
        mock_transcript.language = "en"
        mock_transcript.duration = 10.5
        mock_transcript.segments = []

        mock_client.audio.transcriptions.create.return_value = mock_transcript

        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_audio:
            temp_audio.write(b'fake audio data')
            temp_audio.flush()

            transcriber = WhisperTranscriber(api_key="test_key")
            result = transcriber.transcribe(temp_audio.name)

        self.assertEqual(result['text'], "Test transcription")
        self.assertEqual(result['language'], "en")
        self.assertEqual(result['duration'], 10.5)

    def test_transcribe_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.transcriber.transcribe("nonexistent_file.wav")

    def test_save_transcription_success(self):
        transcription = {
            "text": "Test transcription",
            "language": "en",
            "duration": 10.5
        }

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = self.transcriber.save_transcription(transcription, temp_path)
            self.assertTrue(result)

            with open(temp_path, 'r') as f:
                saved_data = json.load(f)

            self.assertEqual(saved_data['text'], "Test transcription")
        finally:
            os.unlink(temp_path)

    @patch('xscriber.modules.transcriber.openai.OpenAI')
    def test_transcribe_and_save_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_transcript = MagicMock()
        mock_transcript.text = "Test transcription"
        mock_transcript.language = "en"
        mock_transcript.duration = 10.5
        mock_transcript.segments = []

        mock_client.audio.transcriptions.create.return_value = mock_transcript

        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_audio, \
             tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_output:

            temp_audio.write(b'fake audio data')
            temp_audio.flush()
            temp_output_path = temp_output.name

        try:
            transcriber = WhisperTranscriber(api_key="test_key")
            result = transcriber.transcribe_and_save(temp_audio.name, temp_output_path)

            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_output_path))
        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)