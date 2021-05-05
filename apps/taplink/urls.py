from django.urls import path
from .views import (
    GetDeck, GetDeckWithLink, DeckLinkView, DeckAvatarView,
    DeckDescriptionView, DeckMessengerView,  create_deck,
)


urlpatterns = [
    # Taplink deck pages
    path('deck_page/<slug:slug>/', GetDeckWithLink.as_view(),
         name='get_deck_with_link'),
    path('deck_page/', GetDeck.as_view(), name='get_user_deck'),

    # Taplink update handlers
    path('add_deck/', create_deck, name='add_deck'),
    path('deck_avatar/<slug:slug>/', DeckAvatarView.as_view(),
         name='deck_avatar'),
    path('deck_description/<slug:slug>/', DeckDescriptionView.as_view(),
         name='deck_description'),
    path('deck_messenger/<slug:slug>/', DeckMessengerView.as_view(),
         name='deck_messenger'),
    path('add_deck_link/<slug:slug>/', DeckLinkView.as_view(),
         name='add_deck_link'),
]
