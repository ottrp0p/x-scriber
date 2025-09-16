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

def regenerate_f3a2df7f_trd():
    """Regenerate TRD for f3a2df7f using the new comprehensive method"""

    # Initialize project handler
    project_handler = ProjectHandler()

    project_id = "f3a2df7f"

    # Get all transcription files for this project
    transcription_files = [
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_1.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_2.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_3.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_4.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_5.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_6.json",
        "/Users/tracy/Desktop/repos/x-scriber/data/raw-transcriptions/f3a2df7f_transcription_7.json"
    ]

    print("=== Regenerating TRD for f3a2df7f (Comprehensive Method) ===")
    print(f"Project ID: {project_id}")
    print(f"Using {len(transcription_files)} transcription files...")

    # Check which files exist
    existing_files = []
    for transcription_file in transcription_files:
        if os.path.exists(transcription_file):
            existing_files.append(transcription_file)
            print(f"  ✅ Found: {os.path.basename(transcription_file)}")
        else:
            print(f"  ❌ Missing: {os.path.basename(transcription_file)}")

    print(f"\nFound {len(existing_files)} valid transcription files")

    if not existing_files:
        print("❌ No transcription files found. Cannot regenerate TRD.")
        return

    # Check current TRD content
    current_trd = project_handler.get_trd_content(project_id)
    if current_trd:
        print(f"📄 Current TRD length: {len(current_trd)} characters")
        print("📄 Current TRD preview:")
        print("=" * 60)
        print(current_trd[:500] + "..." if len(current_trd) > 500 else current_trd)
        print("=" * 60)
    else:
        print("📄 No existing TRD found")

    print("\n🔄 Starting comprehensive TRD regeneration...")

    # Use the new comprehensive regeneration method
    success = project_handler.regenerate_trd_comprehensive(project_id)

    if success:
        print("✅ Comprehensive TRD regeneration completed successfully!")

        # Show the new TRD content
        new_trd = project_handler.get_trd_content(project_id)
        if new_trd:
            print(f"📄 New TRD length: {len(new_trd)} characters")
            print("📄 New TRD preview:")
            print("=" * 60)
            print(new_trd[:1000] + "..." if len(new_trd) > 1000 else new_trd)
            print("=" * 60)
        else:
            print("❌ No TRD content found after regeneration")
    else:
        print("❌ Comprehensive TRD regeneration failed")

    print("\n=== Regeneration Complete ===")
    print("Check the TRD file at: data/output/f3a2df7f_trd.md")
    print("Cached versions available at: data/output_cache/f3a2df7f_trd_*.md")

if __name__ == "__main__":
    regenerate_f3a2df7f_trd()