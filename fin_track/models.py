from django.db import models
from django.db.models import Sum

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.description}: ${self.amount}"

    @property
    def is_income(self):
        return self.type == 'income'

    @property
    def is_expense(self):
        return self.type == 'expense'
        
    @classmethod
    def total_income(cls):
        return cls.objects.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0

    @classmethod
    def total_expense(cls):
        return cls.objects.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0

    @classmethod
    def balance(cls):
        total_income = cls.total_income()
        total_expense = cls.total_expense()
        return total_income - total_expense
    
