from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('dungeonsanddragonsphotos', image_name, file_object, file_object.size)
        return f"http://localhost:9000/dungeonsanddragonsphotos/{image_name}"
    except Exception as e:
        return {"error": str(e)}
    
def process_file_delete(client, image_name):
    try:
        client.remove_object('dungeonsanddragonsphotos', image_name)
        return {'status': 'success'}
    except Exception as e:
        return {'error': str(e)}

def add_pic(new_character, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = new_character.character_id
    img_obj_name = f"{i}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    new_character.photo_url = result
    new_character.save()

    return Response({"message": "success", "result": result})


def del_pic(character):
    client = Minio(
        endpoint = settings.AWS_S3_ENDPOINT_URL,
        access_key = settings.AWS_ACCESS_KEY_ID,
        secret_key = settings.AWS_SECRET_ACCESS_KEY,
        secure = settings.MINIO_USE_SSL
    )

    
    url = f"{character.character_id}.png"

    res = process_file_delete(client, url)
    if 'error' in res:
        return Response(res)
    
    return Response({'status': 'success'})