from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class DatedModel(models.Model):
    """
    Base mixin that all models use to include requisite date fields.
    """

    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Budget(DatedModel):
    title = models.CharField(max_length=100)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    users = models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name="users", blank=True)

    def __str__(self):
        return self.title

    def calculate_balance(self):
        qs = Budget.objects.filter(id=self.id).annotate(total_expenses=Sum("expenses__amount"))
        total_expenses = qs[0].total_expenses
        if total_expenses:
            self.balance = self.income - total_expenses
        else:
            self.balance = self.income
        self.save(update_fields=["balance"])

    def aggregate_by_expense_category(self):
        agg_expenses = (
            Budget.objects.filter(id=self.id)
            .values("expenses__category")
            .annotate(total=Sum("expenses__amount"))
        )
        category_stats = []
        for exp in agg_expenses:
            category_stats.append(
                {"category": exp["expenses__category"], "total": str(exp["total"])}
            )
        return category_stats

    class Meta:
        ordering = ("-date_created",)


class Expense(DatedModel):
    class CategoryName(models.TextChoices):
        HOUSING = "HOUSING", ("Housing")
        TRANSPORTATION = "TRANSPORTATION", _("Transportation")
        FOOD = "FOOD", _("Food")
        UTILITIES = "UTILITIES", _("Utilities")
        INSURANCE = "INSURANCE", _("Insurance")
        HEALTHCARE = "HEALTHCARE", _("Healthcare")
        INVESTING = "INVESTING", _("Investing")
        ENTERTAINMENT = "ENTERTAINMENT", _("Entertainment")

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CategoryName.choices, null=False)
    amount = models.DecimalField(default=Decimal("0.00"), max_digits=8, decimal_places=2)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="expenses")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.category})"

    class Meta:
        ordering = ("-amount",)


@receiver(post_delete, sender=Expense, dispatch_uid="expense_item_post_delete_signal")
def re_calculate_budget_balance(sender, instance, *args, **kwargs):
    instance.budget.calculate_balance()
