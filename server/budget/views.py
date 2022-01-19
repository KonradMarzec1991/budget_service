from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django_filters import rest_framework as filters

from .models import Budget, Expense
from .serializers import BudgetSerializer, ExpenseSerializer
from .filters import BudgetFilter, ExpenseFilter
from .pagination import BudgetPagination, ExpensePagination
from .permissions import IsOwnerOrAllowed, IsExpenseOwnerOrAllowed


class BudgetViewSet(ModelViewSet):
    permission_classes = (IsOwnerOrAllowed, )

    lookup_field = "id"
    serializer_class = BudgetSerializer
    filterset_class = BudgetFilter
    pagination_class = BudgetPagination

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return Budget.objects.prefetch_related("expenses").all()

        allowed_budgets = list(owner.users.all().values_list("id", flat=True))
        return Budget.objects.filter(
            Q(owner=owner.id) | Q(pk__in=allowed_budgets)
        ).prefetch_related("expenses").all()


class ExpensesViewSet(ModelViewSet):
    permission_classes = (IsExpenseOwnerOrAllowed, )

    lookup_field = "id"
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filterset_class = ExpenseFilter
    pagination_class = ExpensePagination
