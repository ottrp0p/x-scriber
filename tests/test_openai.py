#!/usr/bin/env python
"""
Test script to verify OpenAI integrations are working
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xscriber.modules.transcriber import WhisperTranscriber
from xscriber.modules.chat_completion import ChatCompletionProcessor


def test_chat_completion():
    """Test OpenAI Chat Completions integration"""
    print("🤖 Testing OpenAI Chat Completions...")

    try:
        processor = ChatCompletionProcessor()

        # Test with a simple transcription
        test_transcription = """
        We need to build a user login system. The system should have email and password authentication,
        and it should include password reset functionality. Users should be able to create accounts
        and login securely.
        """

        print("   Processing test transcription...")
        trd_content = processor.process_transcription_to_trd(test_transcription)

        print("✅ Chat Completions working!")
        print(f"   Generated TRD length: {len(trd_content)} characters")
        print("   Sample output:")
        print("   " + trd_content[:200] + "...")

        return True

    except Exception as e:
        print(f"❌ Chat Completions failed: {str(e)}")
        return False


def test_whisper_transcription():
    """Test OpenAI Whisper integration (note: requires actual audio file)"""
    print("🎙️ Testing OpenAI Whisper...")

    try:
        transcriber = WhisperTranscriber()
        print("✅ Whisper client initialized successfully!")
        print("   (Note: Need audio file to test actual transcription)")
        return True

    except Exception as e:
        print(f"❌ Whisper initialization failed: {str(e)}")
        return False


def test_api_endpoints():
    """Test our Django API endpoints"""
    print("🌐 Testing Django API endpoints...")

    try:
        import requests
        base_url = "http://localhost:8000"

        # Test projects list
        response = requests.get(f"{base_url}/api/projects/")
        if response.status_code == 200:
            print("✅ Projects API working!")
            data = response.json()
            print(f"   Found {len(data.get('projects', []))} projects")
        else:
            print(f"❌ Projects API failed: {response.status_code}")
            return False

        # Test project detail
        response = requests.get(f"{base_url}/api/projects/0/")
        if response.status_code == 200:
            print("✅ Project detail API working!")
            data = response.json()
            print(f"   TRD content length: {len(data.get('trd_content', ''))}")
        else:
            print(f"❌ Project detail API failed: {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing X-Scriber OpenAI Integration")
    print("=" * 50)

    tests = [
        test_whisper_transcription,
        test_chat_completion,
        test_api_endpoints
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    print("=" * 50)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("🎉 All tests passed! X-Scriber is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()