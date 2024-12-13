from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Transaction
from .forms import TransactionForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.contrib.auth.models import User
from reportlab.lib import colors
from django.contrib.auth.decorators import login_required
import json
import os
import csv
from django.db.models import Sum
from decimal import Decimal
from io import BytesIO
import base64

from datetime import datetime, timedelta



def landing_page(request):
    return render(request, 'fin_track/landing_page.html')

@login_required
def home(request):

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # Assign the transaction to the logged-in user
            transaction.save()
            return redirect('home')
    else:
        form = TransactionForm()

    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    tot_history = list(transactions)
    trans_history = tot_history[-1:-11:-1]


    user = request.user

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

    context = {
            'total_expense': total_expense,
            'total_income': total_income,
            'balance': balance,
            'trans_history': trans_history,
            'income_labels': income_labels,
            'income_values': income_values,
            'expense_labels': expense_labels,
            'expense_values': expense_values,
            'form': form
        }
    return render(request, 'fin_track/index.html', context)
 
@login_required
def summary(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance
    }
    return render(request, 'fin_track/summary.html', context)

@login_required
def report(request):
    return render(request, 'fin_track/report.html')

@login_required
def download_transactions_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
    else:
        transactions = Transaction.objects.filter(user=request.user)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Description", "Amount", "Type"])

    for transaction in transactions:
        writer.writerow([transaction.date, transaction.description, transaction.amount, transaction.type])

    return response

@login_required
def download_transactions_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        transactions = Transaction.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        )
    else:
        transactions = Transaction.objects.filter(user=request.user)

    # Prepare data for table
    data = [["Date", "Description", "Amount", "Type"]]
    for transaction in transactions:
        data.append([transaction.date, transaction.description, transaction.amount, transaction.type])

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0095ff")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    pdf.build([table])
    return response

@login_required
def download_transactions(request):
    file_type = request.GET.get('file_type')
    if file_type == 'csv':
        return download_transactions_csv(request)
    elif file_type == 'pdf':
        return download_transactions_pdf(request)
