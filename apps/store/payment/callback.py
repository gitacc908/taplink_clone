from django.shortcuts import get_object_or_404


def result_handler(response: dict):#-> PaymentHistory:
    purchase_id = response['order']
    purchase = get_object_or_404(Order, pk=purchase_id)

    if response['status']['code'] != 'success':
        data = {
            "error": True,
            "error_message": "error",  # TODO check error body response
            "transaction_id": response['id'],
        }
    else:
        data = {
            "purchase": purchase,
            "amount": int(response['amount']),
            "transaction_id": response['id'],
        }

    return data
