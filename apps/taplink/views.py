from django.shortcuts import render, HttpResponse, redirect 
from django.http import HttpResponseNotFound
from .models import Deck
from .forms import AvatarForm, BodyForm, MessengerForm
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


class DeckUpdateView(LoginRequiredMixin, View):
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        deck = get_object_or_404(Deck, slug=kwargs['slug'])
        if 'avatar_submit' in request.POST:
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance = deck
                new_form = form.save(commit=False)
                new_form.icon = form.cleaned_data['icon']
                new_form.save(update_fields=['icon'])
                return redirect(deck.get_absolute_url())
        elif 'description_submit' in request.POST:
            form = BodyForm(request.POST)
            if form.is_valid():
                form.instance = deck
                new_form = form.save(commit=False)
                new_form.body = form.cleaned_data['body']
                new_form.save(update_fields=['body'])
                return redirect(deck.get_absolute_url())
        elif 'messenger_submit' in request.POST:
            form = MessengerForm(request.POST)
            if form.is_valid():
                form.instance = deck
                new_form = form.save(commit=False)
                telegram = form.cleaned_data['telegram']
                whatsapp = form.cleaned_data['whatsapp']
                if telegram and whatsapp:
                    new_form.telegram = telegram
                    new_form.whatsapp = whatsapp
                    new_form.save(update_fields=['telegram', 'whatsapp'])
                elif telegram:
                    new_form.telegram = telegram
                    new_form.save(update_fields=['telegram'])
                else:
                    new_form.whatsapp = whatsapp
                    new_form.save(update_fields=['whatsapp'])
                return redirect(deck.get_absolute_url())
        return render(request, 'taplink/index.html', {'obj': deck})


class AddDeckLink(LoginRequiredMixin, UpdateView):
    model = Deck
    template_name = 'taplink/index.html'
    login_url = 'login'
    fields = ['slug']
    success_url = reverse_lazy('get_deck_with_link')

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.object.slug})
