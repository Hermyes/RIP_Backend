# Generated by Django 4.2.4 on 2024-10-10 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField()),
                ('username', models.CharField(max_length=150, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.BooleanField()),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('character_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('race', models.CharField(max_length=20)),
                ('class_field', models.CharField(db_column='class', max_length=14)),
                ('description', models.CharField(max_length=1000)),
                ('features', models.CharField(max_length=150)),
                ('hit_points', models.IntegerField()),
                ('armor_class', models.IntegerField()),
                ('photo_url', models.CharField(max_length=100, null=True, unique=True)),
            ],
            options={
                'db_table': 'character',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CharacterToRequest',
            fields=[
                ('key', models.AutoField(primary_key=True, serialize=False)),
                ('coordinate_x', models.IntegerField(blank=True, null=True)),
                ('coordinate_y', models.IntegerField(blank=True, null=True)),
                ('friendorenemy', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'character_to_request',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('request_id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('deleted', 'Удалён'), ('formed', 'Сформирован'), ('completed', 'Завершён'), ('rejected', 'Отклонён')], default='draft', max_length=10)),
                ('creation_date', models.DateTimeField(blank=True, null=True)),
                ('formation_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('map_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'request',
                'managed': False,
            },
        ),
    ]