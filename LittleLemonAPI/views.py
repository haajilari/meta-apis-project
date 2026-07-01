from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
from .permissions import is_manager


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering_fields = ['id', 'title']
    search_fields = ['title']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]


class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['category', 'featured']
    ordering_fields = ['price', 'title']
    search_fields = ['title', 'category__title']

    def get_permissions(self):
        return [IsAuthenticated()]

    def post(self, request, *args, **kwargs):
        if not is_manager(request.user):
            self.permission_denied(
                request,
                message='You are not authorized to add menu items.'
            )
        return super().post(request, *args, **kwargs)


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def put(self, request, *args, **kwargs):
        if not is_manager(request.user):
            self.permission_denied(
                request,
                message='You are not authorized to update menu items.'
            )
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            self.permission_denied(
                request,
                message='You are not authorized to update menu items.'
            )
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not is_manager(request.user):
            self.permission_denied(
                request,
                message='You are not authorized to delete menu items.'
            )
        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_denied(
            request,
            message='POST is not allowed on a single menu item.'
        )