from rest_framework import permissions


def is_manager(user):
    return user.groups.filter(name='Manager').exists()


def is_delivery_crew(user):
    return user.groups.filter(name='Delivery crew').exists()


def is_customer(user):
    return (
        user.is_authenticated
        and not is_manager(user)
        and not is_delivery_crew(user)
    )


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_manager(request.user)


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_delivery_crew(request.user)


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and is_customer(request.user)