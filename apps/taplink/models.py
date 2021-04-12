from django.db import models
from apps.users.models import CustomUser


# Deck for taplink 
class Deck(models.Model):
    """
    Stores a single icon field, related to :model:`apps.users.CustomUser`
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='icons')

    class Meta:
        verbose_name = 'Deck'
        verbose_name_plural = "Decks"


class Body(models.Model):
    """
    Stores a single body field, related to :model:`apps.taplink.Deck`
    """
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    body = models.TextField(verbose_name='Text')

    class Meta:
        verbose_name = 'Text'
        verbose_name_plural = "Texts"


class Messenger(models.Model):
    """
    Stores a single messenger field, related to :model:`apps.taplink.Deck`
    """
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    messenger = models.CharField(max_length=255, verbose_name='Messanger')

    class Meta:
        verbose_name = 'Messenger'
        verbose_name_plural = "Messengers"
