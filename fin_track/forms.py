from django import forms
from .models import Transaction, Budget, TotalIncome


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'description', 'amount']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'total_budget', 'actual']

class TotalForm(forms.ModelForm):
    class Meta:
        model = TotalIncome
        fields = ['total_income']
