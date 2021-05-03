from django.urls import path
from .views import ( GetDeck, DeckUpdateView,
                     GetDeckWithLink, AddDeckLink,
                     create_deck )


urlpatterns = [
    # Taplink deck pages
    path('deck_page/<slug:slug>/', GetDeckWithLink.as_view(), 
                                   name='get_deck_with_link'),
    path('deck_page/', GetDeck.as_view(), name='get_user_deck'),

    # Taplink update handlers
    path('add_deck/', create_deck, name='add_deck'),
    path('deck_update/<slug:slug>/', DeckUpdateView.as_view(),
                                     name='deck_update'),
    path('add_deck_link/<slug:slug>/', AddDeckLink.as_view(), 
                                       name='add_deck_link'),
]
