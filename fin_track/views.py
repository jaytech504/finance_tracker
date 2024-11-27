from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Transaction, LinkedCard
from .forms import TransactionForm
from .yodlee_utils import get_yodlee_access_token, fetch_transactions
from .utils import save_yodlee_transactions
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64



# Create your views here.
def home(request):
    total_income = Transaction.total_income()
    total_expense = Transaction.total_expense()
    balance = Transaction.balance()
    tot_history = list(Transaction.objects.all())
    trans_history = tot_history[-1:-6:-1]

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
        plt.figure(figsize=(8, 4))
        plt.plot(df_grouped.index, df_grouped.values, marker='o', linestyle='-', color='blue')
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
        plt.figure(figsize=(8, 4))
        plt.plot(in_df_grouped.index, in_df_grouped.values, marker='o', linestyle='-', color='blue')
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
            'total_expense': total_expense,
            'total_income': total_income,
            'balance': balance,
            'graph': graph,
            'in_graph': in_graph,
            'trans_history': trans_history,
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

def link_bank_card(request):
    """
    Generate a FastLink URL for users to link their bank card.
    """
    # Get Yodlee access token
    access_token = get_yodlee_access_token()

    # Generate the FastLink URL
    fastlink_url = "https://sandbox.yodlee.com/ysl/fastlink/v1/"  # Update for production
    app_token = access_token  # Yodlee uses the same token as an app token
    user_token = access_token  # Replace with actual user token for production

    # Example parameters to pass to FastLink
    fastlink_params = {
        "app_token": app_token,
        "user_token": user_token,
        "extra_params": {
            "configName": "Aggregation"  # Example config for fetching transactions
        }
    }

    # Redirect or render a template to display FastLink
    return render(request, "link_bank_card.html", {"fastlink_url": fastlink_url, "params": fastlink_params})


def save_linked_card(request):
    """
    Save the linked card details to the database.
    """
    if request.method == "POST":
        card_data = json.loads(request.body)

        # Save card details (example fields, modify as needed)
        LinkedCard.objects.create(
            account_name=card_data.get("accountName"),
            account_number=card_data.get("accountNumber"),
            provider_name=card_data.get("providerName"),
            user=request.user  # Link to the logged-in user
        )

        return JsonResponse({"message": "Card details saved successfully."}, status=201)

    return JsonResponse({"error": "Invalid request method."}, status=400)