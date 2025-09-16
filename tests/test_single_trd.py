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

def test_single_trd_update():
    """Test single TRD update with first transcription"""

    # Initialize project handler
    project_handler = ProjectHandler()

    project_id = "5872053c"
    transcription_file = "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/5872053c_transcription_1.json"

    print("=== Testing Single TRD Update ===")
    print(f"Project ID: {project_id}")
    print(f"Transcription: {transcription_file}")

    # Check if file exists
    if not os.path.exists(transcription_file):
        print(f"  ❌ File not found: {transcription_file}")
        return

    # Queue the transcription for TRD processing
    print(f"  📋 Queuing transcription for TRD update...")
    project_handler.trd_update_queue.put((project_id, transcription_file))
    print(f"  ✅ Queued successfully. Queue size: {project_handler.trd_update_queue.qsize()}")

    # Give some time for processing
    print("Waiting 10 seconds for processing...")
    import time
    time.sleep(10)

    print("=== Test Complete ===")

if __name__ == "__main__":
    test_single_trd_update()