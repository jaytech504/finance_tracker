from .models import Transaction

def save_yodlee_transactions(transactions):
    """
    Save Yodlee transactions to the database.
    """
    for transaction in transactions:
        Transaction.objects.create(
            title=transaction.get("description", "Bank Transaction"),
            amount=abs(transaction.get("amount", 0)),
            transaction_type="Income" if transaction.get("amount", 0) > 0 else "Expense",
            date=transaction.get("transactionDate"),
            source="Yodlee",
        )