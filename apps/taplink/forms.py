from django import forms 
from .models import Deck


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['icon',]


class BodyForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['body',]
