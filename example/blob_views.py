import json
import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from zipfile import ZipFile

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.storage.queue import QueueServiceClient
from azure.core.exceptions import ResourceNotFoundError

from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = "endpoint-container"
AZURE_QUEUE_NAME = "tasks"  # Added for consistency

def list_view(request):
    return render(request, 'example/list.html')

def get_blobs(request):
    prefix = request.GET.get('prefix', '')
    conn_str = AZURE_CONNECTION_STRING
    container_name = AZURE_CONTAINER_NAME
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_client = blob_service.get_container_client(container_name)
    items = []
    parent = '#' if not prefix else prefix  # Fixed: Keep trailing '/' for dir IDs
    for blob_or_prefix in container_client.walk_blobs(name_starts_with=prefix, delimiter='/'):
        rel_name = blob_or_prefix.name[len(prefix):] if prefix else blob_or_prefix.name
        full_id = blob_or_prefix.name
        if full_id.endswith('/'):
            items.append({
                "id": full_id,
                "parent": parent,
                "text": rel_name.rstrip('/'),
                "children": True,
                "type": "dir"
            })
        else:
            items.append({
                "id": full_id,
                "parent": parent,
                "text": rel_name,
                "children": False,
                "type": "file"
            })
    return JsonResponse(items, safe=False)

@csrf_exempt
def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        paths = data.get('paths', [])
        if not paths:
            return JsonResponse({"error": "No paths selected"}, status=400)
        task_id = str(uuid.uuid4())
        queue_service = QueueServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        queue_client = queue_service.get_queue_client(AZURE_QUEUE_NAME)
        message = json.dumps({
            "task_id": task_id,
            "paths": paths
        })
        try:
            queue_client.send_message(message)
        except ResourceNotFoundError:
            queue_client.create_queue()
            queue_client.send_message(message)
        return JsonResponse({"task_id": task_id})
    return HttpResponse(status=405)

@csrf_exempt
def download_file(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        filenames = data.get('filenames')  # Now expect a list (array) of filenames
        if not filenames:
            return JsonResponse({"error": "No filenames provided"}, status=400)
        if not isinstance(filenames, list):
            filenames = [filenames]  # Handle single filename for backward compatibility

        blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service.get_container_client(AZURE_CONTAINER_NAME)

        if len(filenames) == 1:
            # Single file: Download directly
            blob_client = container_client.get_blob_client(filenames[0])
            if not blob_client.exists():
                return JsonResponse({"error": "Blob not found"}, status=404)
            stream = blob_client.download_blob()
            response = HttpResponse(stream.readall(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filenames[0])}"'
            return response
        else:
            # Multiple files: Create ZIP in memory
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, 'w') as zip_file:
                for filename in filenames:
                    blob_client = container_client.get_blob_client(filename)
                    if blob_client.exists():
                        stream = blob_client.download_blob()
                        zip_file.writestr(os.path.basename(filename), stream.readall())
                    else:
                        # Skip missing blobs or handle error as needed
                        pass
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="files.zip"'
            return response
    return HttpResponse(status=405)

def status(request, task_id):
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(AZURE_CONTAINER_NAME)
    prefix = f"{task_id}/"
    blobs = list(container_client.list_blobs(name_starts_with=prefix))
    progress_blob = container_client.get_blob_client(f"{task_id}/progress.txt")
    try:
        progress = float(progress_blob.download_blob().readall().decode('utf-8'))
        if progress >= 100:  # Explicitly check for completion
            return JsonResponse({"status": "done", "progress": 100})
    except (ResourceNotFoundError, ValueError):
        progress = min((len(blobs) / 3) * 100, 100) if len(blobs) else 0
    if len(blobs) == 3:
        return JsonResponse({"status": "done", "progress": 100})
    return JsonResponse({"status": "pending", "progress": progress})

def count_files(request):
    prefix = request.GET.get('prefix', '')
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service.get_container_client(AZURE_CONTAINER_NAME)
    blobs = list(container_client.list_blobs(name_starts_with=prefix))
    file_count = len([b for b in blobs if not b.name.endswith('/')])
    return JsonResponse({"count": file_count})

@csrf_exempt
def cancel_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        if not task_id:
            return JsonResponse({"error": "No task_id provided"}, status=400)
        blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service.get_container_client(AZURE_CONTAINER_NAME)
        blob_client = container_client.get_blob_client(f"{task_id}/status.txt")
        blob_client.upload_blob("canceled", overwrite=True)
        
        # Delete the queue message
        queue_service = QueueServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        queue_client = queue_service.get_queue_client(AZURE_QUEUE_NAME)
        messages = queue_client.receive_messages(max_messages=1, visibility_timeout=5)  # Short timeout to peek
        for msg in messages:
            msg_data = json.loads(msg.content)
            if msg_data.get('task_id') == task_id:
                queue_client.delete_message(msg)
                break
        
        return JsonResponse({"status": "canceled"})
    return HttpResponse(status=405)

@csrf_exempt
def get_state(request):
    task_state = request.session.get('task_state', {'isActive': False, 'taskId': None})
    return JsonResponse(task_state)

@csrf_exempt
def update_state(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Validate minimally
        if 'isActive' not in data or 'taskId' not in data:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        request.session['task_state'] = data
        return JsonResponse({'status': 'updated'})
    return HttpResponse(status=405)