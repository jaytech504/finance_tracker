import requests
from django.conf import settings

# Get Yodlee API credentials
CLIENT_ID = settings.YODLEE_CLIENT_ID
CLIENT_SECRET = settings.YODLEE_CLIENT_SECRET
API_URL = settings.YODLEE_API_URL

def get_yodlee_access_token():
    """
    Fetch Yodlee access token.
    """
    url = f"{API_URL}/auth/token"
    headers = {"Api-Version": "1.1", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"clientId": CLIENT_ID, "secret": CLIENT_SECRET}
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raise an error if the request fails
    return response.json().get("token")


def add_user(access_token, username, email):
    """
    Register a user with Yodlee.
    """
    url = f"{API_URL}/user/register"
    headers = {
        "Api-Version": "1.1",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    data = {
        "user": {
            "loginName": username,
            "email": email,
            "locale": "en_US",
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def fetch_transactions(access_token, start_date, end_date):
    """
    Fetch transactions from Yodlee.
    """
    url = f"{API_URL}/transactions"
    headers = {
        "Api-Version": "1.1",
        "Authorization": f"Bearer {access_token}",
    }
    params = {"fromDate": start_date, "toDate": end_date}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("transaction", [])  # Return the list of transactions