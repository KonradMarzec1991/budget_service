import pytest


@pytest.fixture
def budget_input():
    return {"title": "BUDGET-1", "income": "1500"}


@pytest.fixture
def expense_input():
    return {"title": "Doctor_visit", "category": "HEALTHCARE", "amount": "200"}
