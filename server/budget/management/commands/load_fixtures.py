import json
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from budget.models import Budget, Expense


def load_users(file_path):
    with open(os.path.join(file_path, "users.json")) as f:
        dict_data = json.load(f)
        data = dict_data["users"]

        for item in data:
            get_user_model().objects.create_user(**item["fields"])


def load_budgets(file_path):
    with open(os.path.join(file_path, "budgets.json")) as f:
        dict_data = json.load(f)
        data = dict_data["budgets"]

        instances = []
        for item in data:
            fields = item["fields"]
            username = fields.pop("owner")

            instances.append(
                Budget(**fields, owner=get_user_model().objects.get(username=username))
            )
        Budget.objects.bulk_create(instances)


def load_expenses(file_path):
    with open(os.path.join(file_path, "expenses.json")) as f:
        dict_data = json.load(f)
        data = dict_data["expenses"]

        instances = []
        for item in data:
            fields = item["fields"]
            budget_title = fields.pop("budget")
            username = fields.pop("owner")

            instances.append(
                Expense(
                    **fields,
                    budget=Budget.objects.get(title=budget_title),
                    owner=get_user_model().objects.get(username=username),
                )
            )
        Expense.objects.bulk_create(instances)


class Command(BaseCommand):
    help = "Upload objects (users, budgets, expenses) from json file"

    def handle(self, *args, **kwargs):

        # manual
        path = f"{os.getcwd()}/fixtures/"
        # path = f"{os.getcwd()}/server/fixtures/"

        try:
            if get_user_model().objects.exists():
                self.stdout.write(self.style.SUCCESS("DB already populated."))
                return

            load_users(path)
            load_budgets(path)
            load_expenses(path)

            budgets = Budget.objects.all()
            for budget in budgets:
                budget.calculate_balance()

            self.stdout.write(self.style.SUCCESS("Fixture uploading completed."))
        except IOError:
            self.stdout.write(
                self.style.WARNING(f"Unable to read file {path} or file contains wrong data.")
            )
