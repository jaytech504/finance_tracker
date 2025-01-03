from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    CATEGORIES = (
        ('food', 'Food'),
        ('transportation', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('rent', 'Rent'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORIES, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.description} ({self.type}) - {self.amount}"

    @property
    def is_income(self):
        return self.type == 'income'

    @property
    def is_expense(self):
        return self.type == 'expense'
        


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=255, null=True, blank=True)  # New name field
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    difference = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0.00)



    def save(self, *args, **kwargs):
        # Automatically calculate the difference
        self.difference = self.total_budget - self.actual
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.user.username}'s Budget: {self.total_budget}"

