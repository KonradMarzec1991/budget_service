from rest_framework import serializers
from dateutil.parser import isoparse

from .models import Budget, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = (
            "id", "owner", "title", "category", "amount", "budget"
        )

    def get_owner(self, value):
        return self.context['request'].user.id  #TODO

    def create(self, validated_data):
        owner = self.context['request'].user
        expense = Expense.objects.create(owner=owner, **validated_data)
        return expense


class BudgetSerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True)

    class Meta:
        model = Budget
        fields = (
            "id", "date_created", "title", "owner", "users", "income", "balance", "expenses"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['date_created'] = isoparse(representation['date_created']).strftime("%Y-%M-%d %H:%m:%S")
        return representation
