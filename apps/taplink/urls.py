from django.urls import path
from .views import ( GetDeck, AddMessengerView, 
                    AddAvatarView, AddDescriptionView, 
                    GetDeckWithLink, AddDeckLink,
                    create_deck)


urlpatterns = [
    # Taplink deck pages
    path('deck_page/<slug:slug>/', GetDeckWithLink.as_view(), 
                                                    name='get_deck_with_link'),
    path('deck_page/', GetDeck.as_view(), name='get_user_deck'),

    # Taplink update handlers
    path('add_deck/', create_deck, name='add_deck'),
    path('add_messenger/<slug:slug>/', AddMessengerView.as_view(), 
                                                        name='add_messenger'),
    path('add_avatar/<slug:slug>/', AddAvatarView.as_view(), name='add_avatar'),
    path('add_description/<slug:slug>/', AddDescriptionView.as_view(), 
                                                        name='add_description'),
    path('add_deck_link/<slug:slug>/', AddDeckLink.as_view(), 
                                                        name='add_deck_link'),
]
