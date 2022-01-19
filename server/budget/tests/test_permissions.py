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
def test_user_not_added_to_budget_has_not_access():
    owner_1 = OwnerFactory(id=1, is_superuser=False)
    owner_2 = OwnerFactory(id=2, is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.get(
        reverse("budgets-detail", args=(budget_1.id,)),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_user_added_to_budget_has_access():
    owner_1 = OwnerFactory(id=1, is_superuser=False)
    owner_2 = OwnerFactory(id=2, is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))

    response = client.patch(
        reverse("budgets-detail", args=(budget_1.id,)), data={"users": [owner_2.id]}
    )

    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.get(
        reverse("budgets-detail", args=(budget_1.id,)),
    )

    assert response.status_code == HTTPStatus.OK
    data = response.data

    assert data["owner"] == 1
    assert data["users"] == [2]


@pytest.mark.django_db
def test_user_added_to_budget_can_modify():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))

    response = client.patch(
        reverse("budgets-detail", args=(budget_1.id,)), data={"users": [owner_2.id]}
    )

    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.patch(
        reverse("budgets-detail", args=(budget_1.id,)),
        data={"income": 200, "title": "modified-title"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.data

    assert data["title"] == "modified-title"
    assert data["income"] == "200.00"


@pytest.mark.django_db
def test_user_added_to_budget_cannot_modify_existing_expenses():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)
    expense_1 = ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=20)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))

    response = client.patch(
        reverse("budgets-detail", args=(budget_1.id,)), data={"users": [owner_2.id]}
    )

    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.patch(
        reverse("expenses-detail", args=(expense_1.id,)), data={"title": "PLANT", "amount": 30}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.django_db
def test_user_added_to_budget_can_add_other_expenses():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=20, owner=owner_1)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))

    response = client.patch(
        reverse("budgets-detail", args=(budget_1.id,)), data={"users": [owner_2.id]}
    )

    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_2))
    response = client.post(
        reverse("expenses-list"),
        data={
            "title": "another_plant",
            "category": "HOUSING",
            "amount": "30.00",
            "budget": budget_1.id,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.data

    assert data == {
        "id": 2,
        "owner": owner_2.id,
        "title": "another_plant",
        "category": "HOUSING",
        "amount": "30.00",
        "budget": budget_1.id,
    }

    response = client.get(
        reverse("budgets-detail", args=(budget_1.id,)),
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.data["expenses"]) == 2


@pytest.mark.django_db
def test_budget_owner_can_remove_other_expenses():
    owner_1 = OwnerFactory(is_superuser=False)
    owner_2 = OwnerFactory(is_superuser=False)

    budget_1 = BudgetFactory(owner=owner_1, income=100)
    ExpenseFactory(budget=budget_1, title="plant", category="HOUSING", amount=20, owner=owner_1)
    expense_2 = ExpenseFactory(
        budget=budget_1, title="plant", category="HOUSING", amount=50, owner=owner_2
    )

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Bearer " + get_tokens_for_user(owner_1))
    response = client.delete(reverse("expenses-detail", args=(expense_2.id,)))

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.data

    budget_1.refresh_from_db()
    assert str(budget_1.balance) == "80.00"
