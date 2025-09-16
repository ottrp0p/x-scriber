from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import tempfile
from pydub import AudioSegment
from .modules.project_handler import ProjectHandler

project_handler = ProjectHandler()


def index(request):
    return render(request, 'xscriber/index.html')


def project_list(request):
    try:
        projects = project_handler.list_projects()
        return JsonResponse({'projects': projects})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def project_detail(request, project_id):
    try:
        metadata = project_handler.get_project_metadata(project_id)
        if not metadata:
            return JsonResponse({'error': 'Project not found'}, status=404)

        trd_content = project_handler.get_trd_content(project_id)

        return JsonResponse({
            'project_id': project_id,
            'metadata': metadata,
            'trd_content': trd_content
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def transcription_list(request, project_id):
    try:
        transcriptions = project_handler.get_transcriptions(project_id)
        return JsonResponse({'transcriptions': transcriptions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def transcription_detail(request, project_id, chunk_id):
    try:
        transcriptions = project_handler.get_transcriptions(project_id)
        transcription = next((t for t in transcriptions if t['chunk_id'] == int(chunk_id)), None)

        if not transcription:
            return JsonResponse({'error': 'Transcription not found'}, status=404)

        return JsonResponse({'transcription': transcription})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def start_recording(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')

            if not project_id:
                return JsonResponse({'error': 'project_id is required'}, status=400)

            success = project_handler.start_recording(project_id)

            if success:
                return JsonResponse({'status': 'recording_started', 'project_id': project_id})
            else:
                return JsonResponse({'error': 'Failed to start recording'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def stop_recording(request):
    if request.method == 'POST':
        try:
            success = project_handler.stop_recording()

            if success:
                return JsonResponse({'status': 'recording_stopped'})
            else:
                return JsonResponse({'error': 'Failed to stop recording'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_project(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', 'New Project')
            description = data.get('description', '')

            project_id = project_handler.create_project(name, description)
            metadata = project_handler.get_project_metadata(project_id)

            return JsonResponse({
                'project_id': project_id,
                'metadata': metadata
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def upload_audio_chunk(request):
    if request.method == 'POST':
        try:
            project_id = request.POST.get('project_id')
            chunk_number = request.POST.get('chunk_number')
            audio_file = request.FILES.get('audio_chunk')

            if not all([project_id, chunk_number, audio_file]):
                return JsonResponse({'error': 'Missing required parameters'}, status=400)

            # Create temporary file for the uploaded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_webm:
                for chunk in audio_file.chunks():
                    temp_webm.write(chunk)
                temp_webm_path = temp_webm.name

            try:
                # Try to convert WebM to WAV using pydub (requires ffmpeg)
                try:
                    audio = AudioSegment.from_file(temp_webm_path, format="webm")

                    # Ensure the output directory exists
                    output_dir = os.path.join('data', 'audio-recordings')
                    os.makedirs(output_dir, exist_ok=True)

                    # Save as WAV file
                    filename = f"{project_id}_audiochunk_{chunk_number}.wav"
                    wav_path = os.path.join(output_dir, filename)

                    # Export as WAV with settings compatible with Whisper
                    audio.export(wav_path, format="wav", parameters=["-ar", "16000"])

                    file_size = os.path.getsize(wav_path)
                    duration = len(audio) / 1000.0

                except Exception as conversion_error:
                    # Fallback: Save WebM directly and let OpenAI handle it
                    print(f"Audio conversion failed (ffmpeg not available): {conversion_error}")
                    output_dir = os.path.join('data', 'audio-recordings')
                    os.makedirs(output_dir, exist_ok=True)

                    filename = f"{project_id}_audiochunk_{chunk_number}.webm"
                    webm_path = os.path.join(output_dir, filename)

                    # Copy the temp file to final location
                    import shutil
                    shutil.copy2(temp_webm_path, webm_path)

                    file_size = os.path.getsize(webm_path)
                    duration = None  # Can't determine without conversion
                    wav_path = webm_path  # Use WebM path for transcription

                # Queue the file for transcription (works with WebM too)
                full_path = os.path.abspath(wav_path)
                project_handler._queue_transcription(project_id, full_path)

                return JsonResponse({
                    'status': 'success',
                    'filename': filename,
                    'size': file_size,
                    'duration': duration,
                    'format': 'wav' if filename.endswith('.wav') else 'webm',
                    'note': 'Using WebM format - install ffmpeg for WAV conversion' if filename.endswith('.webm') else None
                })

            except Exception as e:
                return JsonResponse({'error': f'Audio processing failed: {str(e)}'}, status=500)

            finally:
                # Clean up temporary file
                if os.path.exists(temp_webm_path):
                    os.unlink(temp_webm_path)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)