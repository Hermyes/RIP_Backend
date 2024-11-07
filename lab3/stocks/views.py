from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework import status
from stocks.minio import *
from stocks.serializers import *
from stocks.models import Character, Request, CustomUser, CharacterToRequest
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from stocks.permissions import IsManager, IsAdmin, IsAuth
from django.views.decorators.csrf import csrf_exempt
import redis
import uuid
import random
from django.contrib.auth.models import AnonymousUser
from .getUser import getUserBySession


REDIS_HOST = 'localhost'
REDIS_PORT = 6379

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            # Устанавливаем классы разрешений
            self.permission_classes = classes
            user = getUserBySession(self.request)
            if user == AnonymousUser():
                return Response({"detail": "Authentication credentials were not provided."}, status=401)
            else:
                try:
                    self.check_permissions(self.request)
                except Exception:
                    return Response({"detail": "You do not have permission to perform this action."}, status=403)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator





class userProfile(APIView):
    model = get_user_model()
    serializer_class = UserSerializer

    @swagger_auto_schema(request_body=serializer_class)
    @method_permission_classes((IsAdmin,))
    def put(self, request, pk):
        user1 = get_object_or_404(self.model, pk = pk)
        serialized = self.serializer_class(user1, data=request.data, partial = True)
        if serialized.is_valid():
            if 'password' in serialized.validated_data:
                user1.set_password(serialized.validated_data.get('password'))
                user1.save()
            serialized.save()
            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    # """Класс, описывающий методы работы с пользователями
    # Осуществляет связь с таблицей пользователей в базе данных
    # """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
# Регистрация
    def create(self, request):
        # """
        # Функция регистрации новых пользователей
        # Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        # """
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# Логин
@permission_classes([AllowAny])
@authentication_classes([])
@swagger_auto_schema(
    method='post',
    request_body=UserSerializer
)
@api_view(['POST'])
def login_view(request):
    email = request.data["email"] 
    password = request.data["password"]
    user = authenticate(request, email=email, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, email)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")


@csrf_exempt
@permission_classes([IsAuth])
@authentication_classes([])
@api_view(['POST'])
def logout_view(request):
    logout(request)
    response = HttpResponse("{'status': 'ok'}")
    response.delete_cookie("session_id")
    return response

class CharacterList(APIView):
    model_class = Character
    serializer_class = CharacterSerializer

    @swagger_auto_schema(
        operation_description="Получить список всех персонажей",
        responses={200: CharacterSerializer(many=True)}
    )
    def get(self, request, format=None):
        searchText = request.query_params.get('CharacterName', '')
        searchResult = Character.objects.filter(name__icontains=searchText)
        user1 = getUserBySession(self.request)
        if user1 != AnonymousUser():
            draftReq = user1.request_creator.filter(status='draft').first()
            if draftReq:
                CharacterOnMapCount = CharacterToRequest.objects.filter(request_id = draftReq).count()
                CharacterOnMapID = draftReq.request_id
            else:
                CharacterOnMapCount = 0
                CharacterOnMapID = ''
        else:
            wishCount = 0
            wishID = ''
        serial_data = self.serializer_class(searchResult, many = True)
        return Response({'characters': serial_data.data, 'CharacterOnMapID': CharacterOnMapID, 'CharacterOnMapCount': CharacterOnMapCount})

    
    @swagger_auto_schema(
        operation_description="Создать нового персонажа",
        request_body=CharacterSerializer,
        responses={
            201: CharacterSerializer(),
            400: openapi.Response(description="Неверные данные")
        }
    )
    @method_permission_classes((IsAdmin,))
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class CharacterDetail(APIView):
    model_class = Character
    serializer_class = CharacterSerializer


    @swagger_auto_schema(
        operation_description="Получить детали персонажа",
        responses={200: CharacterSerializer()}
    )
    def get(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        serializer = self.serializer_class(character)
        return Response(serializer.data)
    
    @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(
        operation_description="Обновить детали персонажа",
        request_body=CharacterSerializer,
        responses={200: CharacterSerializer()}
    )   
    def put(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        serializer = self.serializer_class(character, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAdmin,))
    @swagger_auto_schema(
        operation_description="Удалить персонажа",
        responses={
            204: openapi.Response(description="Персонаж успешно удален"),
            404: openapi.Response(description="Персонаж не найден")
        }
    )
    def delete(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        res = del_pic(character)
        if 'error' in res.data:
            return res
        characterToReq = CharacterToRequest.objects.filter(character_id = character)
        characterToReq.delete()
        character.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(
            operation_description="Добавить персонажа в заявку",
            request_body=CharacterSerializer,
            responses={200: CharacterSerializer()}
            )
    def post(self, request, character_id, format=None):
        user1 = getUserBySession(self.request)
        draft = user1.request_creator.filter(status='draft').first()
        character = get_object_or_404(self.model_class, character_id=character_id)
        if not draft and not(CharacterToRequest.objects.filter(request_id = draft, character_id = character.character_id).exists()):
            draft = Request(creator = user1, creation_date = timezone.now())
            draft.save()
        if not(CharacterToRequest.objects.filter(request_id = draft.request_id, character_id = character.character_id).exists()):
            new_position = CharacterToRequest(request_id = draft.request_id, character_id = character.character_id)
            new_position.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)


class AddImageView(APIView):
    @method_permission_classes(IsAdmin,)
    @swagger_auto_schema(
        operation_description="Добавить изображение к персонажу",
        responses={
            200: openapi.Response(description="Изображение успешно добавлено"),
            404: openapi.Response(description="Персонаж не найден"),
            400: openapi.Response(description="Ошибка при добавлении изображения")
        }
    )
    def post(self, request, character_id, format=None):
        character = get_object_or_404(Character, character_id=character_id)
        pic = request.FILES.get('pic')
        result = add_pic(character, pic)
        if 'error' in result.data:
            return result
        return Response(status=status.HTTP_200_OK)



class RequestList(APIView):
    model_class = Request
    serializer_class = RequestSerializer


    @method_permission_classes((IsAuth,))
    @swagger_auto_schema(
        operation_description="Получить список всех заявок",
        responses={200: RequestSerializer(many=True)}
    )
    def get(self, request, format=None):
        user = getUserBySession(request)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

        requests = self.model_class.objects.exclude(status='Удалён').exclude(status='draft')

        if not user.is_staff and not user.is_superuser:
            requests = requests.filter(creator=user)

        if start_date and end_date:
            requests = requests.filter(creation_date__range=[start_date, end_date])
        
        if status_filter:
            requests = requests.filter(status=status_filter)
        

        serialized_requests = self.serializer_class(requests, many=True)
        return Response(serialized_requests.data)
    

class RequestDetail(APIView):
    model_class = Request
    serializer_class = requestDetailSerializer



    @swagger_auto_schema(
        operation_description="Получить детали заявки",
        responses={200: requestDetailSerializer()}
    )
    def get(self, request, request_id, format=None):
        request = get_object_or_404(self.model_class, request_id=request_id)
        serializer = self.serializer_class(request)
        return Response(serializer.data)
    


    @swagger_auto_schema(
        operation_description="Обновить детали заявки",
        request_body=requestDetailSerializer,
        responses={200: requestDetailSerializer()}
    )
    def put(self, request, request_id, format=None):
        requestO = get_object_or_404(self.model_class, request_id=request_id)
        serializer = self.serializer_class(requestO, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    @swagger_auto_schema(
        operation_description="Удалить заявку",
        responses={
            204: openapi.Response(description="Заявка успешно удалена"),
            404: openapi.Response(description="Заявка не найдена")
        }
    )
    def delete(self, request, request_id, format = None):
        req = get_object_or_404(self.model_class, request_id=request_id)
        req.status = 'Удалён'
        req.save()
        return Response(self.serializer_class(req).data)
    

class SaveRequestByCreatorView(APIView):
    @swagger_auto_schema(
        operation_description="Сохранить заявку создателем",
        request_body=requestDetailSerializer,
        responses={
            200: requestDetailSerializer(),
            400: openapi.Response(description="Неверные данные"),
            404: openapi.Response(description="Заявка не найдена")
        }
    )
    def put(self, request, request_id, format=None):
        req = get_object_or_404(Request, request_id=request_id)
        required_fields = ['map_name']
        serializer = requestDetailSerializer(req, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        missing_fields = [field for field in required_fields if field not in request.data or not request.data[field]]
            
        if missing_fields:
            return Response({'error': f'Пропущенные обязательные поля: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        req.formation_date = timezone.now()
        req.status = 'Сформирован'
        req.save()
        serializer.save()
        return Response(serializer.data)
    

class CompleteOrRejectView(APIView):

    @method_permission_classes((IsManager,))
    @swagger_auto_schema(
        operation_description="Завершить или отклонить заявку",
        request_body=requestDetailSerializer,
        responses={
            200: requestDetailSerializer(),
            400: openapi.Response(description="Неправильное состояние или координаты персонажей совпадают"),
            403: openapi.Response(description="У вас нет разрешения на выполнение этого действия"),
            404: openapi.Response(description="Заявка не найдена")
        }
    )
    def put(self, request, request_id):
        try:
            req = Request.objects.get(request_id=request_id)
        except Request.DoesNotExist:
            return Response({'error': 'Заявка не найдена'}, status=status.HTTP_404_NOT_FOUND)

        print(f"Initial status in DB: {req.status}")

        moderator = request.data.get('moderator')
        action = request.data.get('status')

        print(f"Received status: {action}")
        
        if action not in ['Завершён', 'Отклонён']:
            return Response({'error': 'Неправильное состояние'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'Завершён':
            req.moderator = moderator
            req.completion_date = timezone.now()
            req.rating = random.randint(1, 100)
            characters = CharacterToRequest.objects.filter(request=req)
            coordinates = [(char.coordinate_x, char.coordinate_y) for char in characters]

            if len(coordinates) != len(set(coordinates)):
                return Response({'error': 'Координаты персонажей совпадают'}, status=status.HTTP_400_BAD_REQUEST)
            req.status = 'Завершён'
        
        elif action == 'Отклонён':
            req.moderator = moderator
            req.completion_date = timezone.now()
            req.status = 'Отклонён'
        
        req.save()
        
        serializer = RequestSerializer(req)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CharacterToRequestMethod(APIView):
    model = CharacterToRequest
    serializer_class = CharacterToRequestSerializer


    @swagger_auto_schema(
        operation_description="Удалить персонажа из заявки",
        responses={
            204: openapi.Response(description="Персонаж успешно удален из заявки"),
            404: openapi.Response(description="Персонаж или заявка не найдены")
        }
    )
    def delete(self, request, character_id, request_id, format = None):
        character = get_object_or_404(self.model, character_id = character_id, request_id = request_id)
        character.delete()
        characters = self.model.objects.filter(request_id = request_id)
        return Response(self.serializer_class(characters, many = True).data)
    

    @swagger_auto_schema(
        operation_description="Обновить данные персонажа в заявке",
        request_body=CharacterToRequestSerializer,
        responses={
            202: CharacterToRequestSerializer(),
            400: openapi.Response(description="Неверные данные"),
            404: openapi.Response(description="Персонаж или заявка не найдены")
        }
    )
    @method_permission_classes((IsAuth,))
    def put(self, request, character_id, request_id, format = None):
        character = get_object_or_404(self.model, character_id = character_id, request_id = request_id)
        serializer = self.serializer_class(character, data=request.data)
        if serializer.is_valid():
            serializer.save()
            characters = self.model.objects.filter(request_id = request_id)
            return Response(self.serializer_class(characters, many = True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
