from django.urls import path
from . import views

app_name = 'xscriber'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/projects/', views.project_list, name='project_list'),
    path('api/projects/<str:project_id>/', views.project_detail, name='project_detail'),
    path('api/projects/<str:project_id>/transcriptions/', views.transcription_list, name='transcription_list'),
    path('api/projects/<str:project_id>/transcriptions/<int:chunk_id>/', views.transcription_detail, name='transcription_detail'),
    path('api/recording/start/', views.start_recording, name='start_recording'),
    path('api/recording/stop/', views.stop_recording, name='stop_recording'),
    path('api/create_project/', views.create_project, name='create_project'),
]