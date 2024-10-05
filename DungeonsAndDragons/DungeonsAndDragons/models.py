from django.db import models
from django.contrib.auth import get_user_model

class Character(models.Model):
    character_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=20)
    race = models.CharField(max_length=20)
    class_field = models.CharField(db_column='class', max_length=14)  
    description = models.CharField(max_length=1000)
    features = models.CharField(max_length=150)
    hit_points = models.IntegerField()
    armor_class = models.IntegerField()
    photo_url = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'character'


class CharacterToRequest(models.Model):
    key = models.AutoField(primary_key=True)
    character = models.ForeignKey(Character, models.DO_NOTHING, blank=True, null=True)
    request = models.ForeignKey('Request', models.DO_NOTHING, blank=True, null=True)
    coordinate_x = models.IntegerField(blank=True, null=True)
    coordinate_y = models.IntegerField(blank=True, null=True)
    friendorenemy = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'character_to_request'
        unique_together = (('character_id', 'request_id'),)


class Request(models.Model):
    request_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалён'),
        ('formed', 'Сформирован'),
        ('completed', 'Завершён'),
        ('rejected', 'Отклонён'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    creation_date = models.DateTimeField(blank=True, null=True)
    formation_date = models.DateTimeField(blank=True, null=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    map_name = models.CharField(max_length=20)
    creator_id = models.IntegerField(blank=True, null=True)
    moderator_id = models.IntegerField(blank=True, null=True)
    


    class Meta:
        managed = False
        db_table = 'request'

