from django.contrib import admin
from .models import Character, CharacterToRequest, Request
admin.site.register(Character)
admin.site.register(Request)