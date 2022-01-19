from django.db.models import Q
from django_filters import rest_framework as filters

from .models import Budget, Expense


class BaseFilter(filters.FilterSet):
    title = filters.CharFilter(method="filter_title")

    created_after = filters.DateFilter(field_name="date_created", lookup_expr="gt")
    created_before = filters.DateFilter(field_name="date_created", lookup_expr="lt")

    def filter_title(self, queryset, name, value):
        if value:
            queryset = queryset.filter(title__iexact=value)
        return queryset


class ExpenseFilter(BaseFilter):
    category = filters.CharFilter(method="filter_category")
    q = filters.CharFilter(method="filter_q")

    created_after = filters.DateFilter(field_name="date_created", lookup_expr="gt")
    created_before = filters.DateFilter(field_name="date_created", lookup_expr="lt")

    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Expense
        fields = ("date_created", "min_amount", "max_amount", "title", "q")

    def filter_category(self, queryset, name, value):
        if value:
            queryset = queryset.filter(category__iexact=value)
        return queryset

    def filter_q(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(title__icontains=value) | Q(category__icontains=value))
        return queryset


class BudgetFilter(BaseFilter):
    min_income = filters.NumberFilter(field_name="income", lookup_expr="gte")
    max_income = filters.NumberFilter(field_name="income", lookup_expr="lte")

    min_balance = filters.NumberFilter(field_name="balance", lookup_expr="gte")
    max_balance = filters.NumberFilter(field_name="balance", lookup_expr="lte")

    q = filters.CharFilter(method="filter_q")

    class Meta:
        model = Budget
        fields = ("date_created", "title", "income", "balance", "q")

    def filter_q(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                Q(title__icontains=value)
                | Q(expenses__title__icontains=value)
                | Q(expenses__category__icontains=value)
            )
        return queryset
