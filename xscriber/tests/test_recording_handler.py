import os
import tempfile
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase
from xscriber.modules.recording_handler import RecordingHandler


class RecordingHandlerTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.handler = RecordingHandler(chunk_duration=1, output_dir=self.temp_dir)

    def tearDown(self):
        self.handler.cleanup()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_params(self):
        handler = RecordingHandler()
        self.assertEqual(handler.chunk_duration, 30)
        self.assertEqual(handler.sample_rate, 44100)
        self.assertEqual(handler.channels, 1)
        self.assertFalse(handler.is_recording)

    def test_init_custom_params(self):
        handler = RecordingHandler(chunk_duration=60, output_dir="/tmp/test")
        self.assertEqual(handler.chunk_duration, 60)

    def test_get_next_chunk_number_no_existing_files(self):
        result = self.handler._get_next_chunk_number("test_project")
        self.assertEqual(result, 1)

    def test_get_next_chunk_number_with_existing_files(self):
        for i in [1, 3, 5]:
            filename = f"test_project_audiochunk_{i}.wav"
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write("test")

        result = self.handler._get_next_chunk_number("test_project")
        self.assertEqual(result, 6)

    def test_get_audio_chunks_empty(self):
        chunks = self.handler.get_audio_chunks("nonexistent_project")
        self.assertEqual(len(chunks), 0)

    def test_get_audio_chunks_with_files(self):
        filenames = ["test_project_audiochunk_1.wav", "test_project_audiochunk_3.wav", "test_project_audiochunk_2.wav"]
        for filename in filenames:
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write("test")

        chunks = self.handler.get_audio_chunks("test_project")
        self.assertEqual(len(chunks), 3)

        chunk_numbers = [int(os.path.basename(chunk).split('_')[-1].split('.')[0]) for chunk in chunks]
        self.assertEqual(chunk_numbers, [1, 2, 3])

    def test_set_chunk_saved_callback(self):
        callback = MagicMock()
        self.handler.set_chunk_saved_callback(callback)
        self.assertEqual(self.handler.on_chunk_saved_callback, callback)

    def test_is_recording_active(self):
        self.assertFalse(self.handler.is_recording_active())
        self.handler.is_recording = True
        self.assertTrue(self.handler.is_recording_active())

    def test_get_current_project_id(self):
        self.assertIsNone(self.handler.get_current_project_id())
        self.handler.current_project_id = "test_project"
        self.assertEqual(self.handler.get_current_project_id(), "test_project")

    @patch('xscriber.modules.recording_handler.pyaudio.PyAudio')
    def test_start_recording_success(self, mock_pyaudio):
        mock_audio_interface = MagicMock()
        mock_pyaudio.return_value = mock_audio_interface

        mock_stream = MagicMock()
        mock_audio_interface.open.return_value = mock_stream

        result = self.handler.start_recording("test_project")
        self.assertTrue(result)
        self.assertTrue(self.handler.is_recording)
        self.assertEqual(self.handler.current_project_id, "test_project")

        self.handler.stop_recording()

    def test_start_recording_already_recording(self):
        self.handler.is_recording = True
        self.handler.current_project_id = "existing_project"

        result = self.handler.start_recording("new_project")
        self.assertFalse(result)
        self.assertEqual(self.handler.current_project_id, "existing_project")

    @patch('xscriber.modules.recording_handler.pyaudio.PyAudio')
    def test_start_recording_failure(self, mock_pyaudio):
        mock_pyaudio.side_effect = Exception("Audio error")

        result = self.handler.start_recording("test_project")
        self.assertFalse(result)
        self.assertFalse(self.handler.is_recording)

    def test_stop_recording_not_recording(self):
        result = self.handler.stop_recording()
        self.assertFalse(result)

    @patch('xscriber.modules.recording_handler.pyaudio.PyAudio')
    def test_stop_recording_success(self, mock_pyaudio):
        mock_audio_interface = MagicMock()
        mock_pyaudio.return_value = mock_audio_interface

        mock_stream = MagicMock()
        mock_audio_interface.open.return_value = mock_stream

        self.handler.start_recording("test_project")
        time.sleep(0.1)  # Give recording thread time to start

        result = self.handler.stop_recording()
        self.assertTrue(result)
        self.assertFalse(self.handler.is_recording)
        self.assertIsNone(self.handler.current_project_id)