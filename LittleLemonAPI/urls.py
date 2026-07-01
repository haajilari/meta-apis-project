from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoryListCreateView.as_view()),

    path('menu-items', views.MenuItemListCreateView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),
]