# Generated by Django 4.0.1 on 2022-01-18 15:56

from decimal import Decimal

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now=True)),
                ("date_modified", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=100)),
                ("income", models.DecimalField(decimal_places=2, max_digits=10)),
                ("balance", models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "ordering": ("-date_created",),
            },
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now=True)),
                ("date_modified", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=100)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("HOUSING", "Housing"),
                            ("TRANSPORTATION", "Transportation"),
                            ("FOOD", "Food"),
                            ("UTILITIES", "Utilities"),
                            ("INSURANCE", "Insurance"),
                            ("HEALTHCARE", "Healthcare"),
                            ("INVESTING", "Investing"),
                            ("ENTERTAINMENT", "Entertainment"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=8),
                ),
                (
                    "budget",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expenses",
                        to="budget.budget",
                    ),
                ),
            ],
            options={
                "ordering": ("-amount",),
            },
        ),
    ]
