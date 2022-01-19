from random import choice

from django.conf import settings
from factory import declarations, django, fuzzy

from budget.models import Budget, Expense


class OwnerFactory(django.DjangoModelFactory):
    username = declarations.Sequence(lambda n: "username-{}".format(n))
    is_superuser = True

    class Meta:
        model = settings.AUTH_USER_MODEL


class BudgetFactory(django.DjangoModelFactory):
    title = declarations.Sequence(lambda n: "budget-{}".format(n))
    income = fuzzy.FuzzyDecimal(1000, 5000, 2)
    owner = declarations.SubFactory(OwnerFactory)

    class Meta:
        model = Budget


class ExpenseFactory(django.DjangoModelFactory):
    title = declarations.Sequence(lambda n: "expense-{}".format(n))
    category = choice(
        ["HOUSING", "FOOD", "TRANSPORTATION", "INVESTING", "HEALTHCARE", "INSURANCE"]
    )
    amount = fuzzy.FuzzyDecimal(20, 300, 2)
    budget = declarations.SubFactory(BudgetFactory)
    owner = declarations.SubFactory(OwnerFactory)

    class Meta:
        model = Expense
