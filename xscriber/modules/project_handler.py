import os
import json
import uuid
import threading
import queue
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from django.conf import settings

from .transcriber import WhisperTranscriber
from .chat_completion import ChatCompletionProcessor
from .recording_handler import RecordingHandler


class ProjectHandler:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else settings.DATA_DIR
        self.metadata_dir = self.data_dir / 'project_metadata'
        self.audio_dir = self.data_dir / 'audio-recordings'
        self.transcription_dir = self.data_dir / 'raw-transcriptions'
        self.output_dir = self.data_dir / 'output'
        self.output_cache_dir = self.data_dir / 'output_cache'

        self._ensure_directories()

        self.transcriber = WhisperTranscriber()
        self.chat_processor = ChatCompletionProcessor()
        self.recording_handler = RecordingHandler()

        self.transcription_queue = queue.Queue()
        self.trd_update_queue = queue.Queue()
        self.worker_threads = []
        self.is_processing = False

        self._start_worker_threads()

    def _ensure_directories(self):
        for directory in [self.metadata_dir, self.audio_dir, self.transcription_dir, self.output_dir, self.output_cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _start_worker_threads(self):
        self.is_processing = True

        transcription_worker = threading.Thread(target=self._transcription_worker, daemon=True)
        trd_worker = threading.Thread(target=self._trd_update_worker, daemon=True)

        transcription_worker.start()
        trd_worker.start()

        self.worker_threads = [transcription_worker, trd_worker]

    def _stop_worker_threads(self):
        self.is_processing = False

        self.transcription_queue.put(None)
        self.trd_update_queue.put(None)

        for thread in self.worker_threads:
            thread.join(timeout=5.0)

    def create_project(self, name: str, description: str = "") -> str:
        project_id = str(uuid.uuid4())[:8]

        metadata = {
            "project_id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "chunk_count": 0,
            "transcription_count": 0
        }

        metadata_file = self.metadata_dir / f"{project_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        trd_file = self.output_dir / f"{project_id}_trd.md"
        initial_trd = self.chat_processor.generate_trd_document({})
        with open(trd_file, 'w') as f:
            f.write(initial_trd)

        print(f"Created project '{name}' with ID: {project_id}")
        return project_id

    def get_project_metadata(self, project_id: str) -> Optional[Dict[str, Any]]:
        metadata_file = self.metadata_dir / f"{project_id}_metadata.json"
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading project metadata: {str(e)}")
            return None

    def update_project_metadata(self, project_id: str, updates: Dict[str, Any]) -> bool:
        metadata = self.get_project_metadata(project_id)
        if not metadata:
            return False

        metadata.update(updates)
        metadata["last_updated"] = datetime.now().isoformat()

        metadata_file = self.metadata_dir / f"{project_id}_metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating project metadata: {str(e)}")
            return False

    def get_project_id(self, name: str) -> Optional[str]:
        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    if metadata.get("name") == name:
                        return metadata.get("project_id")
            except Exception:
                continue
        return None

    def list_projects(self) -> List[Dict[str, Any]]:
        projects = []
        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    projects.append(metadata)
            except Exception as e:
                print(f"Error reading metadata file {metadata_file}: {str(e)}")
                continue

        projects.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        return projects

    def start_recording(self, project_id: str) -> bool:
        if not self.get_project_metadata(project_id):
            print(f"Project {project_id} not found")
            return False

        self.recording_handler.set_chunk_saved_callback(
            lambda audio_path: self._queue_transcription(project_id, audio_path)
        )

        return self.recording_handler.start_recording(project_id)

    def stop_recording(self) -> bool:
        return self.recording_handler.stop_recording()

    def _queue_transcription(self, project_id: str, audio_file_path: str):
        self.transcription_queue.put((project_id, audio_file_path))

    def _transcription_worker(self):
        while self.is_processing:
            try:
                item = self.transcription_queue.get(timeout=1.0)
                if item is None:
                    break

                project_id, audio_file_path = item
                self._process_transcription(project_id, audio_file_path)
                self.transcription_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in transcription worker: {str(e)}")

    def _process_transcription(self, project_id: str, audio_file_path: str):
        try:
            audio_filename = Path(audio_file_path).name
            chunk_id = audio_filename.split('_')[-1].split('.')[0]

            transcription_file = self.transcription_dir / f"{project_id}_transcription_{chunk_id}.json"

            success = self.transcriber.transcribe_and_save(audio_file_path, str(transcription_file))

            if success:
                print(f"Transcription completed for {audio_filename}")
                self.update_project_metadata(project_id, {"transcription_count":
                    self.get_project_metadata(project_id).get("transcription_count", 0) + 1})

                print(f"TRD QUEUE: Adding transcription to TRD update queue: {str(transcription_file)}")
                self.trd_update_queue.put((project_id, str(transcription_file)))
                print(f"TRD QUEUE: Queue size is now: {self.trd_update_queue.qsize()}")
            else:
                print(f"Transcription failed for {audio_filename}")

        except Exception as e:
            print(f"Error processing transcription: {str(e)}")

    def _trd_update_worker(self):
        print("TRD WORKER: TRD update worker thread started")
        while self.is_processing:
            try:
                item = self.trd_update_queue.get(timeout=1.0)
                if item is None:
                    break

                project_id, transcription_file = item
                print(f"TRD WORKER: Processing TRD update for project {project_id}")
                self._update_trd_document(project_id, transcription_file)
                self.trd_update_queue.task_done()
                print(f"TRD WORKER: Completed TRD update for project {project_id}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"TRD WORKER ERROR: Error in TRD update worker: {str(e)}")
                import traceback
                traceback.print_exc()

    def _cache_trd_version(self, project_id: str, existing_trd: str):
        """Cache the current TRD version before updating"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_file = self.output_cache_dir / f"{project_id}_trd_{timestamp}.md"

        try:
            with open(cache_file, 'w') as f:
                f.write(existing_trd)
            print(f"TRD UPDATE: Cached previous version to {cache_file}")
        except Exception as e:
            print(f"TRD UPDATE: Failed to cache TRD version: {str(e)}")

    def _update_trd_document(self, project_id: str, transcription_file: str):
        try:
            print(f"TRD UPDATE: Starting TRD update for project {project_id} with transcription {transcription_file}")

            with open(transcription_file, 'r') as f:
                transcription_data = json.load(f)

            transcription_text = transcription_data.get("text", "")
            if not transcription_text:
                print(f"No text found in transcription file: {transcription_file}")
                return

            print(f"TRD UPDATE: Found transcription text: {transcription_text[:100]}...")

            trd_file = self.output_dir / f"{project_id}_trd.md"
            existing_trd = ""
            if trd_file.exists():
                with open(trd_file, 'r') as f:
                    existing_trd = f.read()
                print(f"TRD UPDATE: Found existing TRD file with {len(existing_trd)} characters")

                # Cache the existing version before updating
                self._cache_trd_version(project_id, existing_trd)
            else:
                print(f"TRD UPDATE: No existing TRD file, creating new one")

            print(f"TRD UPDATE: Calling OpenAI Chat Completions API...")
            updated_trd = self.chat_processor.process_transcription_to_trd(
                transcription_text, existing_trd
            )

            # Write the completely new TRD (replacement, not append)
            with open(trd_file, 'w') as f:
                f.write(updated_trd)

            print(f"TRD UPDATE: Successfully updated TRD document for project {project_id}")

        except Exception as e:
            print(f"TRD UPDATE ERROR: Error updating TRD document: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_trd_content(self, project_id: str) -> str:
        trd_file = self.output_dir / f"{project_id}_trd.md"
        if not trd_file.exists():
            return ""

        try:
            with open(trd_file, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TRD file: {str(e)}")
            return ""

    def get_transcriptions(self, project_id: str) -> List[Dict[str, Any]]:
        transcriptions = []
        for trans_file in self.transcription_dir.glob(f"{project_id}_transcription_*.json"):
            try:
                with open(trans_file, 'r') as f:
                    data = json.load(f)

                chunk_id = trans_file.stem.split('_')[-1]
                transcriptions.append({
                    "chunk_id": int(chunk_id) if chunk_id.isdigit() else chunk_id,
                    "text": data.get("text", ""),
                    "duration": data.get("duration", 0),
                    "language": data.get("language", "unknown"),
                    "file_path": str(trans_file)
                })
            except Exception as e:
                print(f"Error reading transcription file {trans_file}: {str(e)}")
                continue

        transcriptions.sort(key=lambda x: x["chunk_id"])
        return transcriptions

    def cleanup(self):
        self.recording_handler.cleanup()
        self._stop_worker_threads()