from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from datetime import date

from django.urls.base import reverse
from .models import Character, Request, CharacterToRequest
from django.db import connection

user_id=1

def get_active_request_for_user(user_id):
    request = Request.objects.filter(creator_id=user_id, status='draft').first()
    if request is None:
        request = Request.objects.create(creator_id=user_id, status='draft', creation_date=date.today())
    return request

def count_characters(request_id):
    req = CharacterToRequest.objects.filter(request_id=request_id).count()
    if req:
        return req
    return 0

def Characters(request):
    query = request.GET.get('CharacterSearch')
    if query:
        filtered_characters = Character.objects.filter(name__icontains=query)
    else:
        filtered_characters = Character.objects.all()
    request_id = get_active_request_for_user(user_id).request_id
    count = count_characters(request_id)
    return render(request, 'index.html', {'characters': filtered_characters, 'count_characters': count, 'request_id': request_id})

def base(request):
    return render(request, 'base.html')

def characterDetails(request, id):
    character = Character.objects.filter(character_id=id).first()
    return render(request, 'detail.html', {'character': character})

def charactersOnMap(request, id):
    req = Request.objects.get(request_id=id)
    if req.status == 'Удалён':
        return HttpResponse(status=404)

    characters_in_request = []
    coordinates = []
    if req:
        req2=CharacterToRequest.objects.filter(request_id=id)
        for item in req2.all():
            char = item.character
            char_with_coordinates = {
                'id': char.character_id,
                'name': char.name,
                'photo_url': char.photo_url,
                'coordinates': {'x': item.coordinate_x, 'y': item.coordinate_y},
            }
            characters_in_request.append(char_with_coordinates)
            coordinates.append({'coordinate_x': item.coordinate_x, 'coordinate_y': item.coordinate_y})
        map_name = req.map_name
    else:
        map_name = ""
    return render(request, 'request.html', {'characters': characters_in_request, 'map_name': map_name, 'coordinates': coordinates, 'current_request_id': id})



def add_character_to_request_for_user(user_id, character_id):
    request = get_active_request_for_user(user_id)
    CharacterToRequest.objects.get_or_create(request=request, character_id=character_id)


def add_character(request, character_id):
    add_character_to_request_for_user(user_id, character_id)
    return redirect('Characters')


def delete_request(request, request_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE request SET status = 'Удалён' WHERE request_id = %s", [request_id])
    return redirect('Characters')