from stocks.models import Character, Request, AuthUser, CharacterToRequest
from rest_framework import serializers


class RequestSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    moderator = serializers.StringRelatedField()
    
    class Meta:
        model = Request
        fields = [
            "request_id", "status", "creation_date", "formation_date",
            "completion_date", "map_name", "creator", "moderator"
        ]



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = "__all__"






class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Character
        # Поля, которые мы сериализуем
        fields = [
                    "character_id", "name", "race", "class_field", "description",
                    "features", "hit_points", "armor_class", "photo_url"
                ]

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