from stocks.models import Character, Request, CustomUser, CharacterToRequest
from rest_framework import serializers
from collections import OrderedDict
from stocks.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']


    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 


class RequestSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()
    
    class Meta:
        model = Request
        fields = [
            "request_id", "status", "creation_date", "formation_date",
            "completion_date", "map_name", "creator", "moderator"
        ]

    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 





class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Character
        # Поля, которые мы сериализуем
        fields = [
                    "character_id", "name", "race", "class_field", "description",
                    "features", "hit_points", "armor_class", "photo_url"
                    ]
    
        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class CharacterToRequestSerializer(serializers.ModelSerializer):
    character = serializers.SerializerMethodField()

    class Meta:
        model = CharacterToRequest
        fields = [
            "key", "character", "request", "coordinate_x", "coordinate_y", "friendorenemy"
        ]

    def get_character(self, obj):
        character = Character.objects.get(pk=obj.character_id)
        return {
            'character_id': character.character_id,
            'name': character.name,
            'photo_url': character.photo_url
        }
    
    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 

class requestDetailSerializer(serializers.ModelSerializer):
    characters = CharacterToRequestSerializer(source = 'charactertorequest_set', many = True, read_only = True)
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()

    class Meta:
        model = Request
        fields = [
            "request_id", "status", "creation_date", "formation_date",
            "completion_date", "map_name", "creator", "moderator", "characters"
        ]
    
    def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 