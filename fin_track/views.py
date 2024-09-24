from django.shortcuts import render, redirect
from .models import Transaction
from .forms import TransactionForm
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64



# Create your views here.
def home(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm()

    
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    balance = Transaction.balance()
    
    transactions = Transaction.objects.filter(type='expense').values('date', 'amount')

    # Convert transactions to a DataFrame
    df = pd.DataFrame(list(transactions))

    # If there are transactions, proceed to create the graph
    if not df.empty:
        # Convert the date to datetime for easier plotting
        df['date'] = pd.to_datetime(df['date'])

        # Group the data by date and sum the amounts for each date
        df_grouped = df.groupby(df['date'].dt.date)['amount'].sum()

        # Create the plot
        plt.figure(figsize=(10, 5))
        plt.plot(df_grouped.index, df_grouped.values, marker='o', linestyle='-', color='green')
        plt.title('Spending Over Time')
        plt.xlabel('Date')
        plt.ylabel('Total Spending')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot to a BytesIO object and encode it as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graph = base64.b64encode(image_png).decode('utf-8')

    else:
        graph = None

    in_transactions = Transaction.objects.filter(type='income').values('date', 'amount')

    # Convert transactions to a DataFrame
    in_df = pd.DataFrame(list(in_transactions))

    # If there are transactions, proceed to create the graph
    if not in_df.empty:
        # Convert the date to datetime for easier plotting
        in_df['date'] = pd.to_datetime(in_df['date'])

        # Group the data by date and sum the amounts for each date
        in_df_grouped = in_df.groupby(in_df['date'].dt.date)['amount'].sum()

        # Create the plot
        plt.figure(figsize=(10, 5))
        plt.plot(in_df_grouped.index, in_df_grouped.values, marker='o', linestyle='-', color='green')
        plt.title('Income Over Time')
        plt.xlabel('Date')
        plt.ylabel('Total Income')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot to a BytesIO object and encode it as base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        in_graph = base64.b64encode(image_png).decode('utf-8')

    else:
        in_graph = None
    context = {
            'form': form,
            'total_expense': total_expense,
            'total_income': total_income,
            'balance': balance,
            'graph': graph,
            'in_graph': in_graph
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