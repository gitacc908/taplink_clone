from django.shortcuts import render, HttpResponse, redirect 
from django.http import HttpResponseNotFound
from .models import Deck
from .forms import AvatarForm, BodyForm
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
from django.core.paginator import Paginator


class GetDeckWithLink(LoginRequiredMixin, View):
    template_name = 'taplink/index.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        try:
            deck = Deck.objects.get(slug=kwargs['slug'])
        except Deck.DoesNotExist:
            return HttpResponseNotFound('<h1>Page not found</h1>')
        else:
            return render(request, self.template_name, {'obj': deck})


class GetDeck(LoginRequiredMixin, View):
    template_name = 'taplink/index.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        try:
            deck = Deck.objects.get(user=request.user)
            return render(request, self.template_name, {'obj': deck})
        except MultipleObjectsReturned:
            decks = Deck.objects.all()
            paginator = Paginator(decks, 1)
            page_number = request.GET.get('page', 1)
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
            context = {
                'page_object': page,
                'is_paginated': is_paginated,
                'next_url': next_url,
                'prev_url': prev_url,
            }
            return render(request, 'taplink/deck_list.html', context=context)
        except Deck.DoesNotExist:
            return HttpResponseNotFound('<h1>Page not found</h1>')


class AddMessengerView(LoginRequiredMixin, View):
    template_name = 'taplink/index.html'
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        try:
            deck = Deck.objects.get(slug=kwargs['slug'])
        except Deck.DoesNotExist:
            return render(request, self.template_name)
        else:
            deck.telegram = request.POST['telegram']
            deck.whatsapp = request.POST['whatsapp']
            deck.save(update_fields=['telegram', 'whatsapp'])
            return redirect(deck.get_absolute_url())


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
            return render(self.request, self.template_name)
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
            return render(self.request, self.template_name)
        else:
            form.instance = deck
            new_form = form.save(commit=False)
            new_form.body = form.cleaned_data['body']
            new_form.save(update_fields=['body'])
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_deck_with_link', kwargs={'slug': self.kwargs['slug']})


class AddDeckLink(LoginRequiredMixin, View):
    template_name = 'taplink/index.html'
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        try:
            deck = Deck.objects.get(slug=kwargs['slug'])
        except Deck.DoesNotExist:
            return render(request, self.template_name)
        else:
            try:
                deck.slug = request.POST['link_input']
            except IntegrityError:
                messages.error(request, """Deck with this link already exists, 
                                            try another one.""") # TODO display message in template 
                return redirect(deck.get_absolute_url())        # PS.trying to figure out how to make it "not ugly" xD 
            else:
                deck.save(update_fields=['slug'])
                return redirect(deck.get_absolute_url())
