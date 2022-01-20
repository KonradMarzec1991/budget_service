from unittest.mock import Mock

import pytest

from budget.models import Expense
from budget.serializers import BudgetSerializer, ExpenseSerializer
from budget.tests.factories import OwnerFactory


@pytest.mark.django_db
def test_serializer_set_balance_when_budget_is_created(budget_input):
    owner = OwnerFactory(is_superuser=False)
    serializer = BudgetSerializer(
        context={"request": Mock(user=owner)}, data=budget_input
    )

    assert serializer.is_valid()

    instance = serializer.save()
    assert instance.owner == owner
    assert instance.income == instance.balance


@pytest.mark.django_db
def test_serializer_update_balance_when_expense_is_created_or_updated(
    budget_input, expense_input
):
    owner = OwnerFactory(is_superuser=False)
    serializer = BudgetSerializer(
        context={"request": Mock(user=owner)}, data=budget_input
    )
    assert serializer.is_valid()

    budget = serializer.save()
    serializer = ExpenseSerializer(
        context={"request": Mock(user=owner)},
        data={**expense_input, "budget": budget.id},
    )
    assert serializer.is_valid()

    expense = serializer.save()
    budget.refresh_from_db()

    assert budget.income == budget.balance + expense.amount


@pytest.mark.django_db
def test_serializer_update_balance_when_expense_is_deleted(
    budget_input, expense_input
):
    owner = OwnerFactory(id=5, is_superuser=False)
    serializer = BudgetSerializer(
        context={"request": Mock(user=owner)}, data=budget_input
    )
    assert serializer.is_valid()

    budget = serializer.save()
    serializer = ExpenseSerializer(
        context={"request": Mock(user=owner)},
        data={**expense_input, "budget": budget.id},
    )
    assert serializer.is_valid()

    expense = serializer.save()
    budget.refresh_from_db()

    assert budget.income == budget.balance + expense.amount

    Expense.objects.get(id=expense.id).delete()
    budget.refresh_from_db()

    assert budget.income == budget.balance
