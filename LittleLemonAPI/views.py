from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer
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

def is_admin_or_manager(user):
    return user.is_superuser or is_manager(user)


class ManagerUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        manager_group = Group.objects.get_or_create(name='Manager')[0]
        users = User.objects.filter(groups=manager_group)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')

        if not username:
            return Response(
                {'message': 'username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        manager_group = Group.objects.get_or_create(name='Manager')[0]
        manager_group.user_set.add(user)

        return Response(
            {'message': 'user added to the manager group'},
            status=status.HTTP_201_CREATED
        )


class ManagerUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        manager_group = Group.objects.get_or_create(name='Manager')[0]
        manager_group.user_set.remove(user)

        return Response(
            {'message': 'user removed from the manager group'},
            status=status.HTTP_200_OK
        )


class DeliveryCrewUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        delivery_group = Group.objects.get_or_create(name='Delivery crew')[0]
        users = User.objects.filter(groups=delivery_group)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        username = request.data.get('username')

        if not username:
            return Response(
                {'message': 'username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        delivery_group = Group.objects.get_or_create(name='Delivery crew')[0]
        delivery_group.user_set.add(user)

        return Response(
            {'message': 'user added to the delivery crew group'},
            status=status.HTTP_201_CREATED
        )


class DeliveryCrewUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if not is_admin_or_manager(request.user):
            return Response(
                {'message': 'You are not authorized.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        delivery_group = Group.objects.get_or_create(name='Delivery crew')[0]
        delivery_group.user_set.remove(user)

        return Response(
            {'message': 'user removed from the delivery crew group'},
            status=status.HTTP_200_OK
        )