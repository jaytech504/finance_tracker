from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Transaction, LinkedAccount, BankTransaction
from .forms import TransactionForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .utils import save_transactions
import json
import os
from django.db.models import Sum
from decimal import Decimal
from io import BytesIO
import base64

from datetime import datetime, timedelta


# Create your views here.
def home(request):
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    balance = Transaction.balance()
    tot_history = list(Transaction.objects.all())
    trans_history = tot_history[-1:-6:-1]

    transactions = Transaction.objects.all()

    accounts = LinkedAccount.objects.filter(user=request.user)
    bank_transactions = BankTransaction.objects.filter(linked_account__in=accounts)

    # Format data for the template
    transactions_data = [
        {"date": txn.date, "description": txn.description, "amount": txn.amount}
        for txn in bank_transactions
    ]

    # Convert transactions to a DataFrame
    income_data = (
        transactions.filter(type='income')
        .values('date', 'amount')
        .order_by('date')
    )
    expense_data = (
        transactions.filter(type='expense')
        .values('date', 'amount')
        .order_by('date')
    )

    income_labels = [entry['date'].strftime('%Y-%m-%d') for entry in income_data]
    income_values = [float(entry['amount']) for entry in income_data]
    expense_labels = [entry['date'].strftime('%Y-%m-%d') for entry in expense_data]
    expense_values = [float(entry['amount']) for entry in expense_data]

    print(income_values)
    print(expense_values)

    context = {
            'total_expense': total_expense,
            'total_income': total_income,
            'balance': balance,
            'trans_history': trans_history,
            'income_labels': income_labels,
            'income_values': income_values,
            'expense_labels': expense_labels,
            'expense_values': expense_values,
            "accounts": accounts,
            "transactions_data": transactions_data,
        }
    return render(request, 'fin_track/index.html', context)
    
def summary(request):
    transactions = Transaction.objects.all()
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    balance = Transaction.balance()
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    }
    return render(request, 'fin_track/summary.html', context)

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm()

    context = {
        'form': form,
    }

    return render(request, 'fin_track/transaction.html', context)

@csrf_exempt
@login_required
def fetch_transactions(request):
    if request.method == "POST":
        data = json.loads(request.body)
        auth_code = data.get("code")

        try:
            linked_account = save_transactions(request.user, auth_code)
            return JsonResponse({"message": "Transactions saved successfully!", "account": linked_account.account_name})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)