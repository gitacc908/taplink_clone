from django import forms
from .models import Deck
from betterforms.multiform import MultiModelForm


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['icon', ]


class BodyForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['body', ]


class MessengerForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['telegram', 'whatsapp']
