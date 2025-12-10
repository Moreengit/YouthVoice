import requests
import base64
from datetime import datetime
from django.conf import settings

def get_access_token():
    """Get OAuth token from Safaricom"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    auth_str = f"{consumer_key}:{consumer_secret}"
    auth_token = base64.b64encode(auth_str.encode()).decode()

    headers = {'Authorization': f'Basic {auth_token}'}
    response = requests.get(api_url, headers=headers)
    return response.json()['access_token']


def initiate_stk_push(phone_number, amount, account_reference="YouthVoice", transaction_desc="Sponsorship"):
    """Send STK Push to user's phone"""
    passkey = settings.MPESA_PASSKEY
    access_token = get_access_token()

    # Format timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{MPESA_SHORTCODE}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': "application/json"}
    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    return response.json()