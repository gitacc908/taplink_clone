import json
import simplejson
import requests
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.urls import reverse_lazy, reverse


BASE_URL = "https://api.paybox.money/"
CALLBACK_BASE_URL = reverse_lazy('get_payment_response')


def get_url(purchase, description, request) -> str:

    data = {
        "order": f"{purchase.id}",
        "amount": simplejson.dumps(purchase.get_total()),
        "currency": "KGS",
        "description": description,
        "language": "ru",
        "options": {
            "callbacks": {
                "result_url": CALLBACK_BASE_URL + "/api/v1/purchases/payment_response/",
                "check_url": CALLBACK_BASE_URL,
                "cancel_url": CALLBACK_BASE_URL,
                "success_url": CALLBACK_BASE_URL + f"/user/checkout/?status=success&order={purchase.id}",
                "failure_url": CALLBACK_BASE_URL + f"/user/checkout/?status=error&order={purchase.id}",
                "back_url": CALLBACK_BASE_URL,
                "capture_url": CALLBACK_BASE_URL
            }
        }
    }

    response = requests.post(BASE_URL + "v4/payments",
                             json=data,
                             auth=('535456', 'LeFnP16MP6AU6YKc'),
                             headers={'X-Idempotency-Key': f'{purchase.id}'}
                             )

    if response.status_code != status.HTTP_201_CREATED:
        raise ValidationError({"message": "Ошибка при запросе PayBox"})

    data = json.loads(response.content)

    return data['payment_page_url']

# TODO: IMITATE PAYBOX RESP WITH JSON
