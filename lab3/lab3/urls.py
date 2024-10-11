from django.contrib import admin
from stocks import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'characters/', views.CharacterList.as_view(), name='characters-list'),
    path(r'characters/<int:character_id>/', views.CharacterDetail.as_view(), name='character-detail'),
    # path(r'characters/<int:character_id>/put/', views.put, name='characters-put'),
    path('api/characters/<int:character_id>/addImage', views.add_image, name='add-character-image'),

    path('requests/', views.RequestList.as_view(), name='requests-list'),
    path('requests/<int:request_id>', views.RequestDetail.as_view(), name='request-detail'),
    path('requests/<int:request_id>/form', views.saveRequestByCreator, name='request-form'),
    path('requests/<int:request_id>/moderate', views.completeOrReject, name='request-moderate'),


    path('characterOnMap/<int:request_id>/<int:character_id>', views.CharacterToRequestMethod.as_view(), name='character-on-map'),


    path('user/register', views.userMoment.as_view(), name='user-register'),
    path('user/<int:user_id>', views.userMoment.as_view(), name='user-detail'),
    path('user/<int:user_id>/autentification', views.autentification, name='user-autentification'),
    path('user/<int:user_id>/logout', views.logOut, name='user-logout'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
]