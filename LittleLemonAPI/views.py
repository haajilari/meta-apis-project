from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from .permissions import is_manager, is_customer, is_delivery_crew
from rest_framework.pagination import PageNumberPagination

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
    
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_customer(request.user):
            return Response(
                {'message': 'Only customers can access the cart.'},
                status=status.HTTP_403_FORBIDDEN
            )

        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not is_customer(request.user):
            return Response(
                {'message': 'Only customers can add items to the cart.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CartSerializer(data=request.data)

        if serializer.is_valid():
            menuitem = serializer.validated_data['menuitem']
            quantity = serializer.validated_data['quantity']
            unit_price = menuitem.price
            price = unit_price * quantity

            cart_item, created = Cart.objects.update_or_create(
                user=request.user,
                menuitem=menuitem,
                defaults={
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'price': price,
                }
            )

            response_serializer = CartSerializer(cart_item)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not is_customer(request.user):
            return Response(
                {'message': 'Only customers can delete cart items.'},
                status=status.HTTP_403_FORBIDDEN
            )

        Cart.objects.filter(user=request.user).delete()
        return Response(
            {'message': 'cart cleared'},
            status=status.HTTP_200_OK
        )
    
#! ORDER LIST

class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if is_manager(request.user):
            orders = Order.objects.all()
        elif is_delivery_crew(request.user):
            orders = Order.objects.filter(delivery_crew=request.user)
        else:
            orders = Order.objects.filter(user=request.user)

        status_filter = request.query_params.get('status')
        if status_filter is not None:
            if status_filter in ['true', 'True', '1']:
                orders = orders.filter(status=True)
            elif status_filter in ['false', 'False', '0']:
                orders = orders.filter(status=False)

        date_filter = request.query_params.get('date')
        if date_filter:
            orders = orders.filter(date=date_filter)

        ordering = request.query_params.get('ordering', '-id')
        allowed_ordering_fields = [
            'id', '-id',
            'date', '-date',
            'total', '-total',
            'status', '-status',
        ]

        if ordering in allowed_ordering_fields:
            orders = orders.order_by(ordering)
        else:
            orders = orders.order_by('-id')

        paginator = PageNumberPagination()
        paginator.page_size = 2
        paginated_orders = paginator.paginate_queryset(orders, request)

        serializer = OrderSerializer(paginated_orders, many=True)
        return paginator.get_paginated_response(serializer.data)
    def post(self, request):
        if not is_customer(request.user):
            return Response(
                {'message': 'Only customers can place orders.'},
                status=status.HTTP_403_FORBIDDEN
            )

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {'message': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            total = sum(item.price for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                total=total,
                date=timezone.now().date(),
                status=False
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price=item.price
                )

            cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#! ORDER DETAIL

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_order(self, order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return None

    def get(self, request, order_id):
        order = self.get_order(order_id)

        if order is None:
            return Response(
                {'message': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if is_manager(request.user):
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if is_delivery_crew(request.user):
            if order.delivery_crew != request.user:
                return Response(
                    {'message': 'You are not authorized to view this order.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if order.user != request.user:
            return Response(
                {'message': 'You are not authorized to view this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, order_id):
        order = self.get_order(order_id)

        if order is None:
            return Response(
                {'message': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if is_manager(request.user):
            delivery_crew_id = request.data.get('delivery_crew')
            status_value = request.data.get('status')

            if delivery_crew_id is not None:
                try:
                    delivery_user = User.objects.get(id=delivery_crew_id)
                except User.DoesNotExist:
                    return Response(
                        {'message': 'Delivery crew user not found.'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if not is_delivery_crew(delivery_user):
                    return Response(
                        {'message': 'Selected user is not delivery crew.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                order.delivery_crew = delivery_user

            if status_value is not None:
                order.status = status_value

            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if is_delivery_crew(request.user):
            if order.delivery_crew != request.user:
                return Response(
                    {'message': 'You are not authorized to update this order.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            allowed_fields = set(['status'])
            sent_fields = set(request.data.keys())

            if not sent_fields.issubset(allowed_fields):
                return Response(
                    {'message': 'Delivery crew can only update status.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if 'status' in request.data:
                order.status = request.data.get('status')
                order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {'message': 'You are not authorized to update this order.'},
            status=status.HTTP_403_FORBIDDEN
        )

    def put(self, request, order_id):
        return self.patch(request, order_id)

    def delete(self, request, order_id):
        order = self.get_order(order_id)

        if order is None:
            return Response(
                {'message': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not is_manager(request.user):
            return Response(
                {'message': 'Only managers can delete orders.'},
                status=status.HTTP_403_FORBIDDEN
            )

        order.delete()
        return Response(
            {'message': 'order deleted'},
            status=status.HTTP_200_OK
        )
    

class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response(
                {'message': 'username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'message': 'username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            status=status.HTTP_201_CREATED
        )