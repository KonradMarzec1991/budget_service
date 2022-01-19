import pytest

from budget.tests.factories import BudgetFactory, ExpenseFactory


@pytest.mark.django_db
def test_balance_is_set_when_budget_is_created():
    budget = BudgetFactory()

    assert budget.income == budget.balance


@pytest.mark.django_db
def test_balance_is_updated_when_budget_income_is_updated():
    budget = BudgetFactory()
    budget.income = 2500
    budget.save()

    assert budget.income == budget.balance


@pytest.mark.django_db
def test_balance_is_calculated_when_expense_is_created():
    budget = BudgetFactory()
    expense_1 = ExpenseFactory(budget=budget)
    expense_2 = ExpenseFactory(budget=budget)

    assert budget.balance == budget.income - expense_1.amount - expense_2.amount


@pytest.mark.django_db
def test_balance_is_calculated_when_expense_is_deleted():
    budget = BudgetFactory()
    expense_1 = ExpenseFactory(budget=budget)
    expense_2 = ExpenseFactory(budget=budget)

    expense_2.delete()
    assert budget.balance == budget.income - expense_1.amount

    expense_1.delete()
    assert budget.income == budget.balance
