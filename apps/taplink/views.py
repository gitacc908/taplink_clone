from django.shortcuts import render, HttpResponse, redirect
from django.http import HttpResponseNotFound
from .models import Deck
from .forms import (
    AvatarForm, BodyForm, MessengerForm
)
from django.views import View
from django.views.generic import CreateView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect


class GetDeckWithLink(LoginRequiredMixin, DetailView):
    model = Deck
    template_name = 'taplink/index.html'
    context_object_name = 'obj'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(Deck, slug=self.kwargs['slug'])


class GetDeck(LoginRequiredMixin, ListView):
    model = Deck
    template_name = 'taplink/deck_list.html'
    login_url = 'login'
    paginate_by = 1


def create_deck(request):
    deck = Deck.objects.create(user=request.user)
    return redirect('get_deck_with_link', slug=deck.slug)


class DeckMessengerView(LoginRequiredMixin, FormView):
    form_class = MessengerForm
    template_name = 'taplink/index.html'
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def form_valid(self, form):
        deck = get_object_or_404(Deck, slug=self.kwargs['slug'])
        telegram = form.cleaned_data['telegram']
        whatsapp = form.cleaned_data['whatsapp']
        if telegram and whatsapp:
            deck.telegram = telegram
            deck.whatsapp = whatsapp
            deck.save(update_fields=['telegram', 'whatsapp'])
        elif telegram:
            deck.telegram = telegram
            deck.save(update_fields=['telegram'])
        else:
            deck.whatsapp = whatsapp
            deck.save(update_fields=['whatsapp'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug':
                                                     self.kwargs['slug']})


class DeckDescriptionView(LoginRequiredMixin, UpdateView):
    model = Deck
    fields = ['body']
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug':
                                                     self.object.slug})


class DeckAvatarView(LoginRequiredMixin, UpdateView):
    model = Deck
    fields = ['icon']
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug':
                                                     self.object.slug})


class DeckLinkView(LoginRequiredMixin, UpdateView):
    model = Deck
    fields = ['slug']
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug':
                                                     self.object.slug})
