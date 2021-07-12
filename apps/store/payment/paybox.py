import json
import simplejson
import requests

from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.urls import reverse_lazy, reverse
from django.conf import settings


BASE_URL = settings.BASE_URL
CALLBACK_BASE_URL = settings.CALLBACK_BASE_URL
MERCHANT_ID = settings.MERCHANT_ID
PAY_SECRET_KEY = settings.PAY_SECRET_KEY


def get_url(purchase, request) -> str:
    data = {
        "order": f"{purchase.id}",
        "amount": simplejson.dumps(purchase.get_total()),
        "currency": "KGS",
        "description": purchase.comment,
        "language": "ru",
        "user_phone": purchase.phone,
        "options": {
            "callbacks": {
                "result_url": CALLBACK_BASE_URL,
                    # "/api/purchases/payment_response/",
                "check_url": CALLBACK_BASE_URL,
                "cancel_url": CALLBACK_BASE_URL +
                    '/store/',
                "success_url": CALLBACK_BASE_URL +
                    f"/user/checkout/?status=success&order={purchase.id}",
                "failure_url": CALLBACK_BASE_URL +
                    f"/user/checkout/?status=error&order={purchase.id}",
                "back_url": CALLBACK_BASE_URL + '/store/'
            }
        }
    }

    response = requests.post(BASE_URL + "v4/payments",
                             json=data,
                             auth=(MERCHANT_ID, PAY_SECRET_KEY),
                             headers={'X-Idempotency-Key': f'{purchase.id}'}
                             )
    data = json.loads(response.content)
    print(data)
    print(data['payment_page_url'])
    return data['payment_page_url']


def get_payment_info(payment_id: str) -> dict:
    response = requests.get(BASE_URL + f"v4/payments/{payment_id}",
                            auth=(MERCHANT_ID, PAY_SECRET_KEY),
                            headers={
                                'X-Idempotency-Key': f'{str(uuid.uuid4())}'}
                            )
    data = json.loads(response.content)
    return data


def cancel_payment(purchase):
    response = requests.post(BASE_URL + f"payments/{purchase.payment_id}/cancel",
                             json={},
                             auth=(MERCHANT_ID, PAY_SECRET_KEY),
                             headers={'X-Idempotency-Key': f'{purchase.id}'}
                             )
    data = json.loads(response.content)
    return data.get('code', None)
