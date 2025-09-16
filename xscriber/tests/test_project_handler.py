import os
import json
import tempfile
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase
from xscriber.modules.project_handler import ProjectHandler


class ProjectHandlerTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        with patch('django.conf.settings.DATA_DIR', self.temp_dir):
            self.handler = ProjectHandler(data_dir=self.temp_dir)

    def tearDown(self):
        self.handler.cleanup()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_directories(self):
        expected_dirs = ['project_metadata', 'audio-recordings', 'raw-transcriptions', 'output']
        for dirname in expected_dirs:
            dir_path = os.path.join(self.temp_dir, dirname)
            self.assertTrue(os.path.exists(dir_path))

    @patch('xscriber.modules.project_handler.WhisperTranscriber')
    @patch('xscriber.modules.project_handler.ChatCompletionProcessor')
    def test_create_project(self, mock_chat_processor, mock_transcriber):
        mock_chat_processor.return_value.generate_trd_document.return_value = "# Test TRD"

        project_id = self.handler.create_project("Test Project", "Test Description")

        self.assertIsNotNone(project_id)
        self.assertEqual(len(project_id), 8)

        metadata_file = os.path.join(self.temp_dir, 'project_metadata', f'{project_id}_metadata.json')
        self.assertTrue(os.path.exists(metadata_file))

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        self.assertEqual(metadata['name'], "Test Project")
        self.assertEqual(metadata['description'], "Test Description")
        self.assertEqual(metadata['project_id'], project_id)

        trd_file = os.path.join(self.temp_dir, 'output', f'{project_id}_trd.md')
        self.assertTrue(os.path.exists(trd_file))

    def test_get_project_metadata_existing(self):
        project_id = "test123"
        metadata = {
            "project_id": project_id,
            "name": "Test Project",
            "description": "Test Description"
        }

        metadata_file = os.path.join(self.temp_dir, 'project_metadata', f'{project_id}_metadata.json')
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        result = self.handler.get_project_metadata(project_id)
        self.assertEqual(result['project_id'], project_id)
        self.assertEqual(result['name'], "Test Project")

    def test_get_project_metadata_nonexistent(self):
        result = self.handler.get_project_metadata("nonexistent")
        self.assertIsNone(result)

    def test_update_project_metadata(self):
        project_id = "test123"
        metadata = {
            "project_id": project_id,
            "name": "Test Project",
            "chunk_count": 0
        }

        metadata_file = os.path.join(self.temp_dir, 'project_metadata', f'{project_id}_metadata.json')
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        result = self.handler.update_project_metadata(project_id, {"chunk_count": 5})
        self.assertTrue(result)

        updated_metadata = self.handler.get_project_metadata(project_id)
        self.assertEqual(updated_metadata['chunk_count'], 5)
        self.assertIn('last_updated', updated_metadata)

    def test_get_project_id_by_name(self):
        project_id = "test123"
        metadata = {
            "project_id": project_id,
            "name": "Test Project"
        }

        metadata_file = os.path.join(self.temp_dir, 'project_metadata', f'{project_id}_metadata.json')
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        result = self.handler.get_project_id("Test Project")
        self.assertEqual(result, project_id)

        result = self.handler.get_project_id("Nonexistent Project")
        self.assertIsNone(result)

    def test_list_projects(self):
        projects_data = [
            {"project_id": "proj1", "name": "Project 1", "last_updated": "2023-01-01T00:00:00"},
            {"project_id": "proj2", "name": "Project 2", "last_updated": "2023-01-02T00:00:00"}
        ]

        metadata_dir = os.path.join(self.temp_dir, 'project_metadata')
        os.makedirs(metadata_dir, exist_ok=True)

        for data in projects_data:
            metadata_file = os.path.join(metadata_dir, f'{data["project_id"]}_metadata.json')
            with open(metadata_file, 'w') as f:
                json.dump(data, f)

        result = self.handler.list_projects()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['project_id'], 'proj2')  # Should be sorted by last_updated desc

    @patch('xscriber.modules.project_handler.RecordingHandler')
    def test_start_recording_success(self, mock_recording_handler):
        project_id = "test123"
        metadata = {"project_id": project_id, "name": "Test Project"}

        metadata_file = os.path.join(self.temp_dir, 'project_metadata', f'{project_id}_metadata.json')
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

        mock_handler_instance = mock_recording_handler.return_value
        mock_handler_instance.start_recording.return_value = True

        result = self.handler.start_recording(project_id)
        self.assertTrue(result)
        mock_handler_instance.start_recording.assert_called_once_with(project_id)

    def test_start_recording_project_not_found(self):
        result = self.handler.start_recording("nonexistent")
        self.assertFalse(result)

    def test_get_trd_content_existing(self):
        project_id = "test123"
        trd_content = "# Test TRD Document\n\nContent here"

        trd_file = os.path.join(self.temp_dir, 'output', f'{project_id}_trd.md')
        os.makedirs(os.path.dirname(trd_file), exist_ok=True)
        with open(trd_file, 'w') as f:
            f.write(trd_content)

        result = self.handler.get_trd_content(project_id)
        self.assertEqual(result, trd_content)

    def test_get_trd_content_nonexistent(self):
        result = self.handler.get_trd_content("nonexistent")
        self.assertEqual(result, "")

    def test_get_transcriptions(self):
        project_id = "test123"
        transcriptions_data = [
            {"text": "First transcription", "duration": 10.5, "language": "en"},
            {"text": "Second transcription", "duration": 15.2, "language": "en"}
        ]

        transcription_dir = os.path.join(self.temp_dir, 'raw-transcriptions')
        os.makedirs(transcription_dir, exist_ok=True)

        for i, data in enumerate(transcriptions_data, 1):
            trans_file = os.path.join(transcription_dir, f'{project_id}_transcription_{i}.json')
            with open(trans_file, 'w') as f:
                json.dump(data, f)

        result = self.handler.get_transcriptions(project_id)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['chunk_id'], 1)
        self.assertEqual(result[0]['text'], "First transcription")
        self.assertEqual(result[1]['chunk_id'], 2)