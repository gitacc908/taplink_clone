from django.shortcuts import get_object_or_404
from apps.store.choices import STATUS_NEW


def result_handler(response: dict):
    purchase_id = response['order']
    purchase = get_object_or_404(Order, status=STATUS_NEW, pk=purchase_id)

    if response['status']['code'] != 'success':
        data = {
            "error": True,
            "error_message": "error",
            "transaction_id": response['id'],
        }
    else:
        data = {
            "purchase": purchase,
            "amount": int(response['amount']),
            "transaction_id": response['id'],
        }

    return data
