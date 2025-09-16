#!/usr/bin/env python3

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tracy/Desktop/repos/x-scriber')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import our modules
from xscriber.modules.project_handler import ProjectHandler

def simulate_trd_updates():
    """Simulate TRD updates using existing transcription files"""

    # Initialize project handler
    project_handler = ProjectHandler()

    project_id = "5872053c"
    transcription_files = [
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/5872053c_transcription_1.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/5872053c_transcription_2.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/5872053c_transcription_3.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/5872053c_transcription_4.json"
    ]

    print("=== Simulating TRD Updates ===")
    print(f"Project ID: {project_id}")
    print(f"Processing {len(transcription_files)} transcription files...\n")

    for i, transcription_file in enumerate(transcription_files, 1):
        print(f"Update {i}/4: Processing {transcription_file}")

        # Check if file exists
        if not os.path.exists(transcription_file):
            print(f"  ❌ File not found: {transcription_file}")
            continue

        # Queue the transcription for TRD processing
        print(f"  📋 Queuing transcription for TRD update...")
        project_handler.trd_update_queue.put((project_id, transcription_file))
        print(f"  ✅ Queued successfully. Queue size: {project_handler.trd_update_queue.qsize()}")

        # Give some time for processing
        import time
        time.sleep(2)

        print("")

    print("=== Simulation Complete ===")
    print("The TRD worker thread should process these updates automatically.")
    print("Check the Django server logs for TRD processing messages.")

    # Let processing continue for a bit
    print("Waiting 10 seconds for processing...")
    import time
    time.sleep(10)

if __name__ == "__main__":
    simulate_trd_updates()