from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, BaseUserManager
from django.contrib.auth.models import Group, Permission


class NewUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email адрес", unique=True, max_length=254)
    password = models.CharField(max_length=100, verbose_name="Пароль")
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    USERNAME_FIELD = 'email'

    objects = NewUserManager()
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  # Unique related_name to avoid clashes
        blank=True,
        verbose_name='Группы'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Unique related_name to avoid clashes
        blank=True,
        verbose_name='Разрешения'
    )


class Character(models.Model):
    character_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=20)
    race = models.CharField(max_length=20)
    class_field = models.CharField(db_column='class', max_length=14)  
    description = models.CharField(max_length=1000)
    features = models.CharField(max_length=150)
    hit_points = models.IntegerField()
    armor_class = models.IntegerField()
    photo_url = models.CharField(unique=True, max_length=100, null=True)

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
    rating = models.IntegerField(blank=True, null=True)
    creator = models.ForeignKey(CustomUser, models.DO_NOTHING, related_name='request_creator', blank=True, null=True)
    moderator = models.ForeignKey(CustomUser, models.DO_NOTHING, related_name='request_moderator', blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'request'

