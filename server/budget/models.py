from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
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

    def save(self, *args, **kwargs):
        instance = Budget.objects.filter(id=getattr(self,"id",None)).first()
        if instance:
            if instance.income != self.income:
                super().save(*args, **kwargs)
                self.calculate_balance()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-date_created", )


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

    def save(self, *args, **kwargs):
        instance = Expense.objects.filter(id=getattr(self,"id",None)).first()
        if instance:
            if instance.amount != self.amount:
                super().save(*args, **kwargs)
                self.budget.calculate_balance()
        super().save(*args, **kwargs)


    class Meta:
        ordering = ("-amount", )


@receiver(post_save, sender=Budget, dispatch_uid="budget_item_post_save_signal")
def set_balance(sender, instance, created, *args, **kwargs):
    if created:
        instance.balance = instance.income
        instance.save(update_fields=["balance"])


@receiver(post_save, sender=Expense, dispatch_uid="expense_item_post_save_signal")
def re_calculate_budget_balance(sender, instance, created, *args, **kwargs):
    if created:
        instance.budget.balance -= instance.amount
        instance.budget.save(update_fields=["balance"])


@receiver(post_delete, sender=Expense, dispatch_uid="expense_item_post_delete_signal")
def re_calculate_budget_balance2(sender, instance, *args, **kwargs):  # TODO change name
    instance.budget.calculate_balance()
