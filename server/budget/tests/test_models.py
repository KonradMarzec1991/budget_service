import pytest

from budget.tests.factories import BudgetFactory, ExpenseFactory


@pytest.mark.django_db
def test_balance_is_calculated_when_expense_is_deleted():
    budget = BudgetFactory()
    expense_1 = ExpenseFactory(budget=budget)
    expense_2 = ExpenseFactory(budget=budget)

    expense_2.delete()
    assert budget.balance == budget.income - expense_1.amount

    expense_1.delete()
    assert budget.income == budget.balance


@pytest.mark.django_db
def test_categories_are_aggregated():
    budget = BudgetFactory(income=250)
    ExpenseFactory(budget=budget, category="Housing", amount=30)
    ExpenseFactory(budget=budget, category="Housing", amount=50)
    ExpenseFactory(budget=budget, category="Food", amount=100)

    agg = budget.aggregate_by_expense_category()
    assert agg == [{"category": "Food", "total": "100"}, {"category": "Housing", "total": "80"}]
