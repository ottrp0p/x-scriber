from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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