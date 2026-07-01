from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from LittleLemonAPI.views import UserRegistrationView


urlpatterns = [
    path('admin/', admin.site.urls),

    # Required project registration endpoint
    path('api/users/', UserRegistrationView.as_view()),

    # Djoser endpoints
    path('api/users/', include('djoser.urls')),
    path('api/users/', include('djoser.urls.authtoken')),

    # Required project login endpoint
    path('token/login/', obtain_auth_token),

    # Our API endpoints
    path('api/', include('LittleLemonAPI.urls')),
]