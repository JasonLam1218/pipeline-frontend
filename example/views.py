from django.views.decorators.csrf import csrf_exempt  # For testing
from django.shortcuts import render
from django.http import JsonResponse
import json
import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return render(request, 'example/index.html')

@csrf_exempt
def get_sas_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename')
            if not filename:
                return JsonResponse({'error': 'Missing filename'}, status=400)

            # This is obtained from Vercel environment variables, not .env file
            # Set this variable in Vercel environment variables
            conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING') 
            container_name = 'endpoint-container'
            service_client = BlobServiceClient.from_connection_string(conn_str)
            blob_client = service_client.get_blob_client(container=container_name, blob=filename)

            sas_token = generate_blob_sas(
                account_name=blob_client.account_name,
                container_name=container_name,
                blob_name=filename,
                account_key=blob_client.credential.account_key,
                permission=BlobSasPermissions(write=True),
                expiry=datetime.now(timezone.utc) + timedelta(minutes=15)
            )
            sas_url = f"{blob_client.url}?{sas_token}"
            return JsonResponse({'sasUrl': sas_url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=405)