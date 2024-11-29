from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Transaction, LinkedCard
from .forms import TransactionForm
from plaid.api import plaid_api
from plaid.model import *
from plaid import Configuration, ApiClient
import os
from django.db.models import Sum
from decimal import Decimal
import pandas as pd
import matplotlib.pyplot as plt
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
        }
    return render(request, 'fin_track/index.html', context)

def fetch_bank_transactions(request):
    """
    Fetch and save bank transactions via Yodlee.
    """
    # Get Yodlee access token
    access_token = get_yodlee_access_token()

    # Fetch transactions for the past 30 days
    transactions = fetch_transactions(access_token, "2024-10-01", "2024-11-01")

    # Save transactions to the database
    save_yodlee_transactions(transactions)

    return redirect("dashboard")
    
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

def initialize_plaid():
    configuration = Configuration(
        host="https://sandbox.plaid.com",
        api_key={
            "clientId": os.getenv("PLAID_CLIENT_ID"),
            "secret": os.getenv("PLAID_SECRET")
        },
    )
    api_client = ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)

plaid_client = initialize_plaid()

def plaid_link_token(request):
    # Generate a link token for the client
    request_body = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=str(request.user.id)),
        client_name="Voton",
        products=["transactions"],
        country_codes=["US"],
        language="en"
    )
    response = plaid_client.link_token_create(request_body)
    return JsonResponse({"link_token": response["link_token"]})

def exchange_public_token(request):
    if request.method == "POST":
        public_token = request.POST.get("public_token")
        response = plaid_client.item_public_token_exchange(
            PublicTokenExchangeRequest(public_token=public_token)
        )
        access_token = response["access_token"]
        # Store access_token securely for the user
        request.user.profile.plaid_access_token = access_token
        request.user.profile.save()
        return JsonResponse({"message": "Access token saved"})

def fetch_transactions(request):
    if request.user.profile.plaid_access_token:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        request_body = TransactionsGetRequest(
            access_token=request.user.profile.plaid_access_token,
            start_date=start_date,
            end_date=end_date,
        )
        response = plaid_client.transactions_get(request_body)

        transactions = response["transactions"]
        for txn in transactions:
            transaction_type = 'income' if txn["amount"] > 0 else 'expense'
            Transaction.objects.create(
                date=txn["date"],
                amount=abs(txn["amount"]),
                description=txn["name"],
                transaction_type=transaction_type,
                source="plaid",
            )

        return JsonResponse({"message": "Transactions fetched and categorized"})
    else:
        return JsonResponse({"error": "No Plaid access token found"}, status=400)