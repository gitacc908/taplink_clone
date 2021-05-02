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

    def get_context_data(self, **kwargs):
        context = super(GetDeck, self).get_context_data(**kwargs)
        decks = Deck.objects.filter(user=self.request.user)
        paginator = Paginator(decks, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        is_paginated = page.has_other_pages()
        if page.has_previous():
            prev_url = f'?page={page.previous_page_number()}'
        else:
            prev_url = ''
        if page.has_next():
            next_url = f'?page={page.next_page_number()}'
        else:
            next_url = ''
        context['page_object'] = page
        context['is_paginated'] = is_paginated
        context['next_url'] = next_url
        context['prev_url'] = prev_url
        return context


def create_deck(request):
    deck = Deck.objects.create(user=request.user)
    return redirect('get_deck_with_link', slug=deck.slug)


class AddMessengerView(LoginRequiredMixin, FormView):
    template_name = 'taplink/index.html'
    form_class = MessengerForm
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def form_valid(self, form):
        telegram = form.cleaned_data['telegram']
        whatsapp = form.cleaned_data['whatsapp']
        deck = get_object_or_404(Deck, slug=self.kwargs['slug'])
        form.instance = deck
        new_form = form.save(commit=False)
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={
                                                'slug': self.kwargs['slug']})


class AddAvatarView(LoginRequiredMixin, FormView):
    template_name = 'taplink/index.html'
    form_class = AvatarForm
    login_url = 'login'
    success_url = reverse_lazy('get_deck_with_link')

    def form_valid(self, form):
        form = self.form_class(self.request.POST, self.request.FILES)
        try:
            deck = Deck.objects.get(slug=self.kwargs['slug'])
        except Deck.DoesNotExist:
            raise Http404("Object does not exist!")
        else:
            form.instance = deck
            new_form = form.save(commit=False)
            new_form.icon = form.cleaned_data['icon']
            new_form.save(update_fields=['icon'])
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.kwargs['slug']})


class AddDescriptionView(LoginRequiredMixin, FormView):
    template_name = 'taplink/index.html'
    login_url = 'login'
    form_class = BodyForm
    success_url = reverse_lazy('get_deck_with_link')

    def form_valid(self, form):
        try:
            deck = Deck.objects.get(slug=self.kwargs['slug'])
        except Deck.DoesNotExist:
            raise Http404("Object does not exist!")
        else:
            form.instance = deck
            new_form = form.save(commit=False)
            new_form.body = form.cleaned_data['body']
            new_form.save(update_fields=['body'])
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.kwargs['slug']})


class AddDeckLink(LoginRequiredMixin, UpdateView):
    model = Deck
    template_name = 'taplink/index.html'
    login_url = 'login'
    fields = ['slug']
    success_url = reverse_lazy('get_deck_with_link')

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.object.slug})
