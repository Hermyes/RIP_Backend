from django.http import HttpResponse
import redis
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser  # Adjust the import path as necessary

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

def getUserBySession(request):
    ssid = request.COOKIES.get('session_id')
    if ssid:
        try:
            email = session_storage.get(ssid).decode('utf-8')
            user = CustomUser.objects.get(email=email)
        except AttributeError:
            user = AnonymousUser()
    else:
        user = AnonymousUser() 
    return user