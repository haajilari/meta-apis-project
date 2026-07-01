from django.urls import path
from . import views

urlpatterns = [
    path('categories', views.CategoryListCreateView.as_view()),

    path('menu-items', views.MenuItemListCreateView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),

    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:user_id>', views.ManagerUserDetailView.as_view()),

    path('groups/delivery-crew/users', views.DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<int:user_id>', views.DeliveryCrewUserDetailView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
]