from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from stocks.minio import *
from stocks.serializers import *
from stocks.models import Character, Request, AuthUser, CharacterToRequest
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password


def user():
    try:
        user1 = AuthUser.objects.get(id=1)
    except:
        user1 = AuthUser(id=1, first_name="Иван", last_name="Иванов", password=1234, username="user1")
        user1.save()
    return user1





class CharacterList(APIView):
    model_class = Character
    serializer_class = CharacterSerializer

    def get(self, request, format=None):
        searchText = request.query_params.get('CharacterName', '')
        searchResult = Character.objects.filter(name__icontains=searchText)
        user1 = user()
        draftReq = user1.request_creator.filter(status='draft').first()
        if draftReq:
            CharacterOnMapCount = CharacterToRequest.objects.filter(request_id = draftReq).count()
            CharacterOnMapID = draftReq.request_id
        else:
            CharacterOnMapCount = 0
            CharacterOnMapID = ''
        serial_data = self.serializer_class(searchResult, many = True)
        return Response({'characters': serial_data.data, 'CharacterOnMapID': CharacterOnMapID, 'CharacterOnMapCount': CharacterOnMapCount})

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class CharacterDetail(APIView):
    model_class = Character
    serializer_class = CharacterSerializer

    def get(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        serializer = self.serializer_class(character)
        return Response(serializer.data)

    def put(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        serializer = self.serializer_class(character, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, character_id, format=None):
        character = get_object_or_404(self.model_class, character_id=character_id)
        res = del_pic(character)
        if 'error' in res.data:
            return res
        characterToReq = CharacterToRequest.objects.filter(character_id = character)
        characterToReq.delete()
        character.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    def post(self, request, character_id, format=None):
        user1 = user()
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


@api_view(['Post'])
def add_image(request, character_id, format = None):
    character = get_object_or_404(Character, character_id=character_id)
    pic = request.FILES.get('pic')
    result = add_pic(character, pic)
    if 'error' in result.data:
        return result
    return Response(status=status.HTTP_200_OK)

   
# @api_view(['Put'])
# def put(self, request, character_id, format=None):
#     character = get_object_or_404(self.model_class, character_id=character_id)
#     serializer = self.serializer_class(character, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestList(APIView):
    model_class = Request
    serializer_class = RequestSerializer

    def get(self, request, format=None):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')

        requests = self.model_class.objects.exclude(status='Удалён').exclude(status='draft')

        if start_date and end_date:
            requests = requests.filter(creation_date__range=[start_date, end_date])
        
        if status_filter:
            requests = requests.filter(status=status_filter)

        serialized_requests = self.serializer_class(requests, many=True)
        return Response(serialized_requests.data)
    

class RequestDetail(APIView):
    model_class = Request
    serializer_class = requestDetailSerializer

    def get(self, request, request_id, format=None):
        request = get_object_or_404(self.model_class, request_id=request_id)
        serializer = self.serializer_class(request)
        return Response(serializer.data)
    
    def put(self, request, request_id, format=None):
        requestO = get_object_or_404(self.model_class, request_id=request_id)
        serializer = self.serializer_class(requestO, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, request_id, format = None):
        req = get_object_or_404(self.model_class, request_id=request_id)
        req.status = 'Удалён'
        req.save()
        return Response(self.serializer_class(req).data)
    
@api_view(['Put'])    
def saveRequestByCreator(request, request_id, format=None):
    req = get_object_or_404(Request, request_id=request_id)
    required_fields = ['map_name', 'creator']
    serializer = requestDetailSerializer(req, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    missing_fields = [field for field in required_fields if not getattr(req, field)]
        
    if missing_fields:
        return Response({'error': f'Пропущенные обязательные поля: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    req.formation_date = timezone.now()
    req.status = 'Сформирован'
    req.save()
    serializer.save()
    return Response(serializer.data)
    
@api_view(['PUT'])
def completeOrReject(request, request_id):
    try:
        req = Request.objects.get(request_id=request_id)
    except Request.DoesNotExist:
        return Response({'error': 'Заявка не найдена'}, status=status.HTTP_404_NOT_FOUND)

    moderator = request.data.get('moderator')
    action = request.data.get('status') 
    
    if action not in ['completed', 'rejected']:
        return Response({'error': 'Неправильное состояние'}, status=status.HTTP_400_BAD_REQUEST)
    

    if action == 'completed':
        req.moderator = moderator
        req.completion_date = timezone.now()
        
        characters = CharacterToRequest.objects.filter(request=req)
        coordinates = [(char.coordinate_x, char.coordinate_y) for char in characters]

        if len(coordinates) != len(set(coordinates)):
            return Response({'error': 'Координаты персонажей совпадают'}, status=status.HTTP_400_BAD_REQUEST)
        req.status = 'completed'
    
    elif action == 'rejected':
        req.moderator = moderator
        req.completion_date = timezone.now()
        req.status = 'rejected'
    req.save()
    
    serializer = RequestSerializer(req)
    return Response(serializer.data, status=status.HTTP_200_OK)


class CharacterToRequestMethod(APIView):
    model = CharacterToRequest
    serializer_class = CharacterToRequestSerializer

    def delete(self, requset, character_id, request_id, format = None):
        character = get_object_or_404(self.model, character_id = character_id, request_id = request_id)
        character.delete()
        characters = self.model.objects.filter(request_id = request_id)
        return Response(self.serializer_class(characters, many = True).data)
    
    def put(self, request, character_id, request_id, format = None):
        character = get_object_or_404(self.model, character_id = character_id, request_id = request_id)
        serializer = self.serializer_class(character, data=request.data)
        if serializer.is_valid():
            serializer.save()
            characters = self.model.objects.filter(request_id = request_id)
            return Response(self.serializer_class(characters, many = True).data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class userMoment(APIView):
    model = get_user_model()
    serializer_class = UserSerializer

    def post(self, request, format = None):
        serialized = self.serializer_class(data=request.data)
        if serialized.is_valid():
            user1 = self.model.objects.create_user(
                username=serialized.validated_data.get('username'),
                password=serialized.validated_data.get('password'),
                is_superuser=False,
                is_staff=False,
                email=serialized.validated_data.get('email'),
                first_name=serialized.validated_data.get('first_name'),
                last_name=serialized.validated_data.get('last_name'),
                date_joined=timezone.now()
            )
            user_list = self.model.objects.all()
            return Response(self.serializer_class(user_list, many=True).data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, user_id, format=None):
        user1 = get_object_or_404(self.model, id=user_id)
        serialized = self.serializer_class(user1, data=request.data, partial=True)
        
        if serialized.is_valid():
            current_password = request.data.get('current_password')
            if current_password:
                if check_password(current_password, user1.password):
                    return Response({"Детали": "Текущий пароль не совпадает."}, status=status.HTTP_400_BAD_REQUEST)
            serialized.save()
            
            if 'password' in serialized.validated_data:
                user1.set_password(serialized.validated_data.get('password'))
                user1.save()

            return Response(serialized.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['post'])
def autentification(request, user_id, format = None):
    user = get_user_model().objects.get(pk = user_id)
    if user.check_password(request.data.get('password')) and user.username == request.data.get('username'):
        return Response({'Аутентификация': 'Успех'}, status=status.HTTP_200_OK)
    return Response({'Аутентификация': 'Ошибка, неверное имя пользователя или пароль'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['post'])
def logOut(request, user_id, format = None):
    return Response({'Деавторизация': 'Выход из аккаунта'}, status=status.HTTP_401_UNAUTHORIZED)