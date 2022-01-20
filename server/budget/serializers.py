from dateutil.parser import isoparse
from django.db import transaction
from rest_framework import serializers

from .models import Budget, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = ("id", "owner", "title", "category", "amount", "budget")

    def get_owner(self, value):
        return self.context["request"].user.id

    @transaction.atomic
    def create(self, validated_data):
        owner = self.context["request"].user
        expense = Expense.objects.create(owner=owner, **validated_data)
        expense.budget.calculate_balance()

        if expense.budget.balance < 0:
            raise serializers.ValidationError("Income cannot be lower than 0!")

        return expense

    @transaction.atomic
    def update(self, instance, validated_data):
        updated_instance = super().update(instance, validated_data)
        updated_instance.budget.calculate_balance()

        if updated_instance.budget.balance < 0:
            raise serializers.ValidationError("Income cannot be lower than 0!")

        return updated_instance


class BudgetSerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True, required=False)
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            "id",
            "date_created",
            "title",
            "owner",
            "users",
            "income",
            "balance",
            "stats",
            "expenses",
        )
        read_only_fields = ("id", "date_created", "owner", "expenses")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["date_created"] = isoparse(
            representation["date_created"]
        ).strftime("%Y-%M-%d %H:%m:%S")
        return representation

    def get_stats(self, obj):
        return obj.aggregate_by_expense_category()

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        validated_data["balance"] = validated_data["income"]
        budget = super().create(validated_data)
        return budget

    def update(self, instance, validated_data):
        updated_instance = super().update(instance, validated_data)
        updated_instance.calculate_balance()
        return updated_instance
