import requests
from .models import LinkedAccount, BankTransaction

MONO_API_BASE_URL = "https://api.withmono.com"
MONO_SECRET_KEY = "test_sk_dbpmev1pjyiaw87schvc"

def save_transactions(user, auth_code):
    headers = {"Authorization": f"Bearer {MONO_SECRET_KEY}"}

    # Step 1: Exchange auth code for account details
    auth_response = requests.post(f"{MONO_API_BASE_URL}/account/auth", json={"code": auth_code}, headers=headers)
    auth_data = auth_response.json()

    if auth_response.status_code != 200:
        raise Exception(auth_data.get("message", "Error authenticating account"))

    account_id = auth_data["id"]
    account_details = requests.get(f"{MONO_API_BASE_URL}/accounts/{account_id}", headers=headers).json()

    # Step 2: Save linked account
    linked_account, created = LinkedAccount.objects.get_or_create(
        user=user,
        account_id=account_details["id"],
        defaults={
            "account_name": account_details["name"],
            "account_type": account_details["type"],
            "balance": account_details["balance"],
        },
    )

    # Step 3: Fetch and save transactions
    transactions_response = requests.get(f"{MONO_API_BASE_URL}/accounts/{account_id}/transactions", headers=headers)
    transactions_data = transactions_response.json()

    if transactions_response.status_code != 200:
        raise Exception(transactions_data.get("message", "Error fetching transactions"))

    for txn in transactions_data["data"]:
        BankTransaction.objects.get_or_create(
            linked_account=linked_account,
            transaction_id=txn["id"],
            defaults={
                "date": txn["date"],
                "description": txn["narration"],
                "amount": txn["amount"],
                "category": txn.get("category", ""),
            },
        )

    return linked_account
