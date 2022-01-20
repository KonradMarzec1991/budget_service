from rest_framework import permissions

from .models import Budget


class IsOwnerOrAllowed(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user in list(
            obj.users.all()
        )


class IsExpenseOwnerOrAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            user = request.user
            budget_id = request.data["budget"]
            budget = Budget.objects.filter(id=budget_id).first()
            if not budget:
                return False
            return budget.owner == user or user in list(budget.users.all())
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in ("PATCH", "DELETE"):
            return obj.owner == user or obj.budget.owner == user
        if request.method == "GET":
            return (
                obj.owner == user
                or obj.budget.owner == user
                or user in list(obj.budget.users.all())
            )
        return False
