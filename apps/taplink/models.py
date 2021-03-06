from django.db import models
from apps.users.models import CustomUser
from django.urls import reverse
from django.utils.crypto import get_random_string
from autoslug import AutoSlugField


# Deck for taplink
class Deck(models.Model):
    """
    Stores data for deck with 1 FK field,
    related to :model:`apps.users.CustomUser`
    """
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='deck'
    )
    slug = AutoSlugField(
        populate_from='user', unique=True
    )
    icon = models.ImageField(
        upload_to='icons', verbose_name='image',
        null=True, blank=True
    )
    body = models.TextField(
        verbose_name='description', null=True, blank=True
    )
    whatsapp = models.URLField(
        max_length=200, verbose_name='whatsapp',
        null=True, blank=True
    )
    telegram = models.URLField(
        max_length=200, verbose_name='telegram',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Deck'
        verbose_name_plural = "Decks"
        ordering = ['-id']

    def __str__(self):
        return f'Deck with user: {self.user} and id: {self.id}'

    def get_absolute_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.slug})
