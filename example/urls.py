from django.urls import path
from . import views, blob_views
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('', views.index, name='index'),
    path('get-sas-url/', views.get_sas_url, name='get_sas_url'),
    path('list/', blob_views.list_view, name='list'),
    path('get_blobs/', blob_views.get_blobs, name='get_blobs'),
    path('generate/', blob_views.generate, name='generate'),
    path('status/<uuid:task_id>/', blob_views.status, name='status'),
    path('download-file/', blob_views.download_file, name='download_file'),
    path('count-files/', blob_views.count_files, name='count_files'),
    path('cancel-task/', blob_views.cancel_task, name='cancel_task'),
    path('get-state/', blob_views.get_state, name='get_state'),
    path('update-state/', blob_views.update_state, name='update_state'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)