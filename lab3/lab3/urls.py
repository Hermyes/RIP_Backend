from django.contrib import admin
from stocks import views
from django.urls import include, path
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
    path(r'characters/', views.CharacterList.as_view(), name='characters-list'),
    path(r'characters/<int:character_id>/', views.CharacterDetail.as_view(), name='character-detail'),
    # path(r'characters/<int:character_id>/put/', views.put, name='characters-put'),
    path('api/characters/<int:character_id>/addImage', views.AddImageView.as_view(), name='add-character-image'),

    path('requests/', views.RequestList.as_view(), name='requests-list'),
    path('requests/<int:request_id>', views.RequestDetail.as_view(), name='request-detail'),
    path('requests/<int:request_id>/form', views.SaveRequestByCreatorView.as_view(), name='request-form'),
    path('requests/<int:request_id>/moderate', views.CompleteOrRejectView.as_view(), name='request-moderate'),


    path('characterOnMap/<int:request_id>/<int:character_id>', views.CharacterToRequestMethod.as_view(), name='character-on-map'),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login/',  views.login_view, name='login'),
    path('api/user/logout', views.userLogout.as_view(), name='logoutUser'),
    path('user/<int:pk>/', views.userProfile.as_view(), name='putUser'),


    path('admin/', admin.site.urls),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]