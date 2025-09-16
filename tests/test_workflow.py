#!/usr/bin/env python
"""
Test the complete X-Scriber workflow with real OpenAI API
"""
import os
import sys
import json
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xscriber.modules.project_handler import ProjectHandler


def test_complete_workflow():
    """Test the complete workflow: create project -> process transcription -> update TRD"""
    print("🚀 Testing Complete X-Scriber Workflow")
    print("=" * 60)

    # Initialize project handler
    handler = ProjectHandler()

    # Step 1: Create a new project
    print("📋 Step 1: Creating new project...")
    project_id = handler.create_project(
        name="AI Chat System",
        description="Building an AI-powered chat system with real-time responses"
    )
    print(f"✅ Created project: {project_id}")

    # Step 2: Simulate a transcription (what would come from Whisper)
    print("\n🎙️ Step 2: Simulating transcription processing...")

    mock_transcription = {
        "text": """
        We need to build an AI chat system that can handle real-time conversations.
        The system should use WebSockets for live communication and integrate with
        OpenAI's GPT models for generating responses. We need rate limiting to prevent
        abuse, user authentication, and message history storage. The frontend should
        be responsive and work on mobile devices. Security is critical - we need to
        sanitize all user inputs and prevent injection attacks.
        """,
        "language": "english",
        "duration": 45.2,
        "segments": []
    }

    # Save mock transcription
    transcription_file = handler.transcription_dir / f"{project_id}_transcription_1.json"
    with open(transcription_file, 'w') as f:
        json.dump(mock_transcription, f, indent=2)

    print(f"✅ Saved transcription: {transcription_file.name}")

    # Step 3: Process the transcription to update TRD
    print("\n🤖 Step 3: Processing transcription with OpenAI...")

    # Manually trigger TRD update (normally done by worker thread)
    handler._update_trd_document(project_id, str(transcription_file))

    print("✅ TRD updated with Chat Completions")

    # Step 4: Verify the results
    print("\n📄 Step 4: Checking results...")

    # Get the updated TRD content
    trd_content = handler.get_trd_content(project_id)
    print(f"✅ TRD generated: {len(trd_content)} characters")

    # Get transcriptions
    transcriptions = handler.get_transcriptions(project_id)
    print(f"✅ Transcriptions found: {len(transcriptions)}")

    # Get project metadata
    metadata = handler.get_project_metadata(project_id)
    print(f"✅ Project metadata: {metadata['name']}")

    # Step 5: Show sample output
    print("\n📋 Sample TRD Output:")
    print("-" * 40)
    lines = trd_content.split('\n')
    for line in lines[:15]:  # Show first 15 lines
        print(line)
    if len(lines) > 15:
        print("...")

    print("\n" + "=" * 60)
    print("🎉 Complete workflow test successful!")
    print(f"📁 Project ID: {project_id}")
    print(f"📊 TRD Length: {len(trd_content)} characters")
    print(f"🎙️ Transcriptions: {len(transcriptions)}")

    return project_id


if __name__ == "__main__":
    test_complete_workflow()