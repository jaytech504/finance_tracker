from celery import shared_task
from .yodlee_utils import get_yodlee_access_token, fetch_transactions
from .utils import save_yodlee_transactions

@shared_task
def update_yodlee_transactions():
    access_token = get_yodlee_access_token()
    transactions = fetch_transactions(access_token, "2024-11-01", "2024-11-27")
    save_yodlee_transactions(transactions)