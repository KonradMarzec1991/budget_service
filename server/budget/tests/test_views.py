from http import HTTPStatus

import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from budget.tests.factories import BudgetFactory, ExpenseFactory, OwnerFactory


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
def test_qs_is_filtered_with_request_user():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)

    budget_1 = BudgetFactory(title="GENERAL", income=1000, owner=owner_1)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=120)
    ExpenseFactory(budget=budget_1, title="take-away", category="FOOD", amount=50)

    budget_2 = BudgetFactory(title="OTHER", income=2000, owner=owner_2)
    ExpenseFactory(budget=budget_2, title="flower", category="HOUSING", amount=150)

    budget_3 = BudgetFactory(title="HOLIDAY", income=2000, owner=owner_2)
    ExpenseFactory(budget=budget_3, title="insurance_card", category="INSURANCE", amount=220)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))

    response = client.get(reverse("budgets-list"))

    assert response.status_code == HTTPStatus.OK
    assert response.data["num_of_records"] == 1

    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.get(reverse("budgets-list"))

    assert response.status_code == HTTPStatus.OK
    assert response.data["num_of_records"] == 2


@pytest.mark.django_db
def test_admin_read_all_budgets():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)
    owner_3 = OwnerFactory(is_superuser=True)

    budget_1 = BudgetFactory(title="GENERAL", income=1000, owner=owner_1)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=120)

    budget_2 = BudgetFactory(title="SPECIFIC", income=2000, owner=owner_2)
    ExpenseFactory(budget=budget_2, title="flower", category="HOUSING", amount=150)

    budget_3 = BudgetFactory(title="OTHER", income=2000, owner=owner_3)
    ExpenseFactory(budget=budget_3, title="insurance_card", category="INSURANCE", amount=220)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_3))

    response = client.get(reverse("budgets-list"))

    assert response.status_code == HTTPStatus.OK
    assert response.data["num_of_records"] == 3


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filter_value, number_of_records, number_of_pages",
    [
        ("?q=housing", 3, 1),
        ("?q=INSURANCE", 1, 1),
        ("?title=OTHER", 1, 1),
        ("", 5, 2),
        ("?min_income=800", 4, 1),
        ("?min_income=800&max_income=1200", 2, 1),
        ("?p=2&category=housing", 1, 2),
        ("?p=2&category=food", 1, 2),
    ],
)
def test_budget_qs_is_filtered_and_paginated(filter_value, number_of_records, number_of_pages):
    owner = OwnerFactory()

    budget_1 = BudgetFactory(title="GENERAL", income=1000, owner=owner)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=120)
    ExpenseFactory(budget=budget_1, title="take-away", category="FOOD", amount=50)
    ExpenseFactory(budget=budget_1, title="bus", category="TRANSPORTATION", amount=90)
    ExpenseFactory(budget=budget_1, title="cinema", category="ENTERTAINMENT", amount=60)

    budget_2 = BudgetFactory(title="OTHER", income=2000, owner=owner)
    ExpenseFactory(budget=budget_2, title="flower", category="HOUSING", amount=120)
    ExpenseFactory(budget=budget_2, title="fruits", category="FOOD", amount=20)
    ExpenseFactory(budget=budget_2, title="car", category="TRANSPORTATION", amount=300)
    ExpenseFactory(budget=budget_2, title="theater", category="ENTERTAINMENT", amount=150)
    ExpenseFactory(budget=budget_2, title="life_insurance", category="INSURANCE", amount=400)

    budget_3 = BudgetFactory(title="SPECIFIC", income=500, owner=owner)
    ExpenseFactory(budget=budget_3, title="table", category="HOUSING", amount=400)

    budget_4 = BudgetFactory(title="HOLIDAY", income=5000, owner=owner)
    ExpenseFactory(budget=budget_4, title="travel", category="ENTERTAINMENT", amount=4000)

    budget_5 = BudgetFactory(title="BONUS", income=200, owner=owner)
    ExpenseFactory(budget=budget_5, title="petrol", category="TRANSPORTATION", amount=100)

    budget_6 = BudgetFactory(title="CAMPAIGN", income=1200, owner=owner)
    ExpenseFactory(budget=budget_6, title="life_campaign", category="HEALTHCARE", amount=1000)

    url = f"{reverse('budgets-list')}{filter_value}"
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner))

    response = client.get(url)
    queryset = response.data

    assert len(queryset["data"]) == number_of_records
    assert queryset["num_of_pages"] == number_of_pages


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filter_value, number_of_records, number_of_pages",
    [
        ("?p=1", 5, 3),
        ("?p=2", 5, 3),
        ("?p=3", 3, 3),
        ("?category=food", 2, 1),
        ("?q=life", 2, 1),
        ("?q=transport", 3, 1),
        ("?category=food&title=fruits", 1, 1),
        ("?p=1&min_amount=1000", 2, 1),
        ("?min_amount=90&max_amount=160", 5, 1),
    ],
)
def test_expense_qs_is_filtered_and_paginated(filter_value, number_of_records, number_of_pages):
    owner = OwnerFactory()

    budget_1 = BudgetFactory(title="GENERAL", income=1000, owner=owner)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=120)
    ExpenseFactory(budget=budget_1, title="take-away", category="FOOD", amount=50)
    ExpenseFactory(budget=budget_1, title="bus", category="TRANSPORTATION", amount=90)
    ExpenseFactory(budget=budget_1, title="cinema", category="ENTERTAINMENT", amount=60)

    budget_2 = BudgetFactory(title="OTHER", income=2000, owner=owner)
    ExpenseFactory(budget=budget_2, title="flower", category="HOUSING", amount=120)
    ExpenseFactory(budget=budget_2, title="fruits", category="FOOD", amount=20)
    ExpenseFactory(budget=budget_2, title="car", category="TRANSPORTATION", amount=300)
    ExpenseFactory(budget=budget_2, title="theater", category="ENTERTAINMENT", amount=150)
    ExpenseFactory(budget=budget_2, title="life_insurance", category="INSURANCE", amount=400)

    budget_3 = BudgetFactory(title="SPECIFIC", income=500, owner=owner)
    ExpenseFactory(budget=budget_3, title="table", category="HOUSING", amount=400)

    budget_4 = BudgetFactory(title="HOLIDAY", income=5000, owner=owner)
    ExpenseFactory(budget=budget_4, title="travel", category="ENTERTAINMENT", amount=4000)

    budget_5 = BudgetFactory(title="BONUS", income=200, owner=owner)
    ExpenseFactory(budget=budget_5, title="petrol", category="TRANSPORTATION", amount=100)

    budget_6 = BudgetFactory(title="CAMPAIGN", income=1200, owner=owner)
    ExpenseFactory(budget=budget_6, title="life_campaign", category="HEALTHCARE", amount=1000)

    url = f"{reverse('expenses-list')}{filter_value}"
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner))

    response = client.get(url)

    assert len(response.data["data"]) == number_of_records
    assert response.data["num_of_pages"] == number_of_pages
