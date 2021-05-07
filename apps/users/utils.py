import os
from twilio.rest import Client
from django.conf import settings
from django.utils.crypto import get_random_string


account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN
tw_number = settings.TW_NUMBER

client = Client(account_sid, auth_token)


def send_sms(user_code, phone_number):
    message = client.messages.create(
        body=user_code,
        from_=tw_number,
        to=phone_number
    )


def code_generate():
    code = get_random_string(length=6, allowed_chars='1234567890')
    return code
