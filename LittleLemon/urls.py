from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),

    # Djoser user registration endpoints
    path('api/users/', include('djoser.urls')),

    # Djoser token endpoint
    path('api/users/', include('djoser.urls.authtoken')),

    # Required project login endpoint
    path('token/login/', obtain_auth_token),

    # Our API endpoints
    path('api/', include('LittleLemonAPI.urls')),
]