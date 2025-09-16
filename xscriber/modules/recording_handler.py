import os
# import wave
# import pyaudio
import threading
import time
from typing import List, Optional, Callable
from pathlib import Path
from django.conf import settings


class RecordingHandler:
    def __init__(self, chunk_duration: int = 30, output_dir: Optional[str] = None,
                 sample_rate: int = 44100, channels: int = 1, chunk_size: int = 1024):
        self.chunk_duration = chunk_duration
        self.output_dir = Path(output_dir) if output_dir else settings.AUDIO_RECORDINGS_DIR
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        self.is_recording = False
        self.current_project_id = None
        self.chunk_counter = 0
        self.recording_thread = None
        self.audio_stream = None
        self.audio_interface = None

        self.on_chunk_saved_callback: Optional[Callable[[str], None]] = None

        os.makedirs(self.output_dir, exist_ok=True)

    def set_chunk_saved_callback(self, callback: Callable[[str], None]):
        self.on_chunk_saved_callback = callback

    def start_recording(self, project_id: str) -> bool:
        if self.is_recording:
            print(f"Already recording for project {self.current_project_id}")
            return False

        try:
            self.current_project_id = project_id
            self.chunk_counter = self._get_next_chunk_number(project_id)
            self.is_recording = True

            # TODO: Re-enable when PyAudio is installed
            # self.audio_interface = pyaudio.PyAudio()
            # self.audio_stream = self.audio_interface.open(
            #     format=pyaudio.paInt16,
            #     channels=self.channels,
            #     rate=self.sample_rate,
            #     input=True,
            #     frames_per_buffer=self.chunk_size
            # )

            # self.recording_thread = threading.Thread(target=self._recording_loop)
            # self.recording_thread.daemon = True
            # self.recording_thread.start()

            print(f"Mock recording started for project {project_id} (PyAudio not installed)")
            return True
        except Exception as e:
            print(f"Failed to start recording: {str(e)}")
            self.is_recording = False
            return False

    def stop_recording(self) -> bool:
        if not self.is_recording:
            print("Not currently recording")
            return False

        try:
            self.is_recording = False

            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)

            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None

            if self.audio_interface:
                self.audio_interface.terminate()
                self.audio_interface = None

            print(f"Stopped recording for project {self.current_project_id}")
            self.current_project_id = None
            return True
        except Exception as e:
            print(f"Error stopping recording: {str(e)}")
            return False

    def _recording_loop(self):
        frames = []
        chunk_start_time = time.time()

        while self.is_recording:
            try:
                data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)

                if time.time() - chunk_start_time >= self.chunk_duration:
                    self._save_audio_chunk(frames)
                    frames = []
                    chunk_start_time = time.time()

            except Exception as e:
                print(f"Error during recording: {str(e)}")
                break

        if frames:
            self._save_audio_chunk(frames)

    def _save_audio_chunk(self, frames: List[bytes]):
        if not self.current_project_id:
            return

        try:
            filename = f"{self.current_project_id}_audiochunk_{self.chunk_counter}.wav"
            filepath = self.output_dir / filename

            # TODO: Re-enable when PyAudio/wave is installed
            # with wave.open(str(filepath), 'wb') as wf:
            #     wf.setnchannels(self.channels)
            #     wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
            #     wf.setframerate(self.sample_rate)
            #     wf.writeframes(b''.join(frames))

            # Create mock audio file for demonstration
            with open(str(filepath), 'w') as f:
                f.write("Mock audio file - PyAudio not installed")

            print(f"Saved audio chunk: {filename}")

            if self.on_chunk_saved_callback:
                try:
                    self.on_chunk_saved_callback(str(filepath))
                except Exception as e:
                    print(f"Error in chunk saved callback: {str(e)}")

            self.chunk_counter += 1

        except Exception as e:
            print(f"Error saving audio chunk: {str(e)}")

    def _get_next_chunk_number(self, project_id: str) -> int:
        existing_files = list(self.output_dir.glob(f"{project_id}_audiochunk_*.wav"))
        if not existing_files:
            return 1

        max_number = 0
        for file in existing_files:
            try:
                number = int(file.stem.split('_')[-1])
                max_number = max(max_number, number)
            except (ValueError, IndexError):
                continue

        return max_number + 1

    def get_audio_chunks(self, project_id: str) -> List[str]:
        chunk_files = list(self.output_dir.glob(f"{project_id}_audiochunk_*.wav"))
        chunk_files.sort(key=lambda x: int(x.stem.split('_')[-1]) if x.stem.split('_')[-1].isdigit() else 0)
        return [str(f) for f in chunk_files]

    def is_recording_active(self) -> bool:
        return self.is_recording

    def get_current_project_id(self) -> Optional[str]:
        return self.current_project_id

    def cleanup(self):
        self.stop_recording()