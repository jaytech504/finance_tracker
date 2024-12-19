from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Transaction, Budget
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
from datetime import datetime, timedelta
from django.contrib import messages



def landing_page(request):
    return render(request, 'fin_track/landing_page.html')

@login_required
def home(request):

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    form = TransactionForm()
    if request.method == 'POST':
        if 'add_transaction' in request.POST:  # Handle manual transaction form
            form = TransactionForm(request.POST)
            if form.is_valid():
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                return redirect('home')

        elif 'upload_csv' in request.POST:  # Handle CSV upload
            csv_file = request.FILES.get('csv_file')

            # Check if a file was uploaded
            if not csv_file:
                messages.error(request, "Please upload a CSV file.")
                return redirect('home')

            # Check if the file is a CSV
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file type. Please upload a .csv file.")
                return redirect('home')

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                # Check for required columns
                required_columns = {'date', 'description', 'amount', 'type'}
                if not required_columns.issubset(reader.fieldnames):
                    messages.error(
                        request, 
                        f"CSV file is missing required columns. Please ensure your CSV includes: {', '.join(required_columns)}"
                    )
                    return redirect('home')

                # Process rows
                for row in reader:
                    try:
                        # Validate amount
                        amount = float(row['amount'])
                        if row['type'] not in ['income', 'expense']:
                            raise ValueError("Invalid transaction type. Use 'income' or 'expense'.")

                        # Validate date
                        transaction_date = datetime.strptime(row['date'], '%Y-%m-%d')

                        # Create transaction
                        Transaction.objects.create(
                            user=request.user,
                            date=transaction_date,
                            description=row['description'],
                            amount=amount,
                            type=row['type'],
                        )
                    except Exception as e:
                        messages.warning(
                            request, 
                            f"Skipping row due to error: {row}. Error: {str(e)}"
                        )
                messages.success(request, "CSV file uploaded successfully!")
                return redirect('home')

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect('home')

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
    writer.writerow(["date", "description", "amount", "type"])

    for transaction in transactions:
        writer.writerow([transaction.date.strftime('%Y-%m-%d'), transaction.description, transaction.amount, transaction.type])

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

@login_required
def budget_data(request):
    """Serve budget data for the logged-in user."""
    budgets = Budget.objects.filter(user=request.user).values(
        "id", "category", "budgeted_amount", "actual_amount"
    )
    return JsonResponse(list(budgets), safe=False)

@csrf_exempt
@login_required
def update_budget(request):
    """Handle updates made through the Handsontable grid."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON payload
            for row in data:
                budget_id = row.get("id")
                if budget_id:  # Update existing budget
                    budget = Budget.objects.get(id=budget_id, user=request.user)
                    budget.category = row.get("category")
                    budget.budgeted_amount = row.get("budgeted_amount")
                    budget.actual_amount = row.get("actual_amount")
                    budget.save()
                else:  # Create a new budget entry if no ID exists
                    Budget.objects.create(
                        user=request.user,
                        category=row.get("category"),
                        budgeted_amount=row.get("budgeted_amount"),
                        actual_amount=row.get("actual_amount"),
                    )
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@login_required
def budget_page(request):
    return render(request, "fin_track/budget.html")