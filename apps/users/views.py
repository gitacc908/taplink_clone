import json
from django.shortcuts import (
    render, HttpResponse, HttpResponseRedirect, redirect
)
from .forms import (
    NumberForm, CodeForm, CustomUserCreationForm,
    SetPasswordForm, CustomUserChangeForm
)
from twilio.base.exceptions import TwilioRestException
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.views.generic import UpdateView, DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import CustomUser
from django.shortcuts import render, HttpResponse
from django.views import View
from .utils import code_generate, send_sms
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse


class GetNumber(FormView):
    template_name = 'registration/registration-number.html'
    form_class = NumberForm
    success_url = reverse_lazy('verify_view')

    def form_valid(self, form):
        phone = str(form.cleaned_data['phone'])
        try:
            CustomUser.objects.get(phone_number=phone)
            messages.error(self.request, 'This phone is already registered!')
            return render(self.request, self.template_name, {'form': form})
        except CustomUser.DoesNotExist:
            new_user = {
                'code': code_generate(),
                'phone': phone
            }
            try:
                send_sms(new_user['code'], new_user['phone'])
                self.request.session['data'] = new_user
            except TwilioRestException:
                return HttpResponse('Unauthorized!', status=401)
            return super().form_valid(form)


class VerifyCodeView(FormView):
    form_class = CodeForm
    template_name = 'registration/registration-submit.html'
    success_url = reverse_lazy('signup')

    def get_context_data(self, **kwargs):
        kwargs['phone'] = self.request.session['data']['phone']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        typed_code = form.cleaned_data['number']
        code = self.request.session['data']['code']
        if code == typed_code:
            return super().form_valid(form)
        else:
            messages.error(self.request, "Code doesn't match up!")
            return render(self.request, self.template_name, {'form': form})


class SignUpView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('get_profile')

    def form_valid(self, form):
        phone_number = self.request.session['data']['phone']
        user = form.save(commit=False)
        user.phone_number = phone_number
        user.is_active = True
        user.save()
        user = authenticate(
            username=user.phone_number,
            password=form.cleaned_data['password1']
        )
        if user:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('get_profile', kwargs={'pk': self.request.user.pk})


class GetPhoneNumber(FormView):
    form_class = NumberForm
    template_name = 'resetpassword/change_password_with_number.html'
    success_url = reverse_lazy('verify_phone_number')

    def form_valid(self, form):
        phone = str(form.cleaned_data.get('phone'))
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except CustomUser.DoesNotExist:
            messages.error(self.request, 'User does not exist!')
            return render(self.request, self.template_name, {'form': form})
        else:
            reset = {
                'code': code_generate(),
                'phone': phone
            }
            try:
                send_sms(reset['code'], phone)
                self.request.session['reset_data'] = reset
            except TwilioRestException:
                return HttpResponse('Unauthorized!', status=401)
            return super().form_valid(form)


class VerifyPhoneNumber(FormView):
    form_class = CodeForm
    template_name = 'resetpassword/change_password_submit.html'
    success_url = reverse_lazy('reset_password')

    def get_context_data(self, **kwargs):
        kwargs['phone_number'] = self.request.session['reset_data']['phone']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        typed_code = form.cleaned_data['number']
        code = self.request.session['reset_data']['code']
        if typed_code == code:
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Code doesnt match up!')
            return render(self.request, self.template_name, {'form': form})


class ResetPasswordView(View):
    form_class = SetPasswordForm
    template_name = 'resetpassword/change_password.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)

        if form.is_valid():
            user = get_object_or_404(
                CustomUser,
                phone_number=request.session['reset_data']['phone']
            )
            password = form.cleaned_data['new_password1']
            user.password = make_password(password)
            user.save(update_fields=['password'])
            user = authenticate(request, username=user.phone_number,
                                password=password)
            if user:
                login(request, user)
                return redirect('get_profile', request.user.id)
        return render(request, self.template_name, {'form': form})


class GetProfile(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile/edit-profile.html'
    login_url = 'login'
    success_url = reverse_lazy('get_profile')

    def get_success_url(self):
        return reverse('get_profile', kwargs={'pk': self.request.user.pk})


class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('get_profile')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            return super().form_valid(form)
        return render(request, 'registration/login.html', {'form': form})

    def get_success_url(self):
        return reverse('get_profile', kwargs={'pk': self.request.user.pk})


class GetPhoneForUpdate(LoginRequiredMixin, FormView):
    form_class = NumberForm
    template_name = 'profile/change-number.html'
    success_url = reverse_lazy('verify_phone_for_update')
    login_url = 'login'

    def form_valid(self, form):
        phone = str(form.cleaned_data.get('phone'))
        if CustomUser.objects.filter(phone_number=phone).exists():
            messages.error(self.request, 'This phone number already exists!')
            return render(self.request, self.template_name, {'form': form})
        reset_phone = {
            'code': code_generate(),
            'phone': phone,
            'old_phone': str(self.request.user.phone_number)
        }
        try:
            send_sms(reset_phone['code'], reset_phone['old_phone'])
            self.request.session['reset_phone'] = reset_phone
        except TwilioRestException:
            return HttpResponse('Unauthorized!', status=401)
        return super().form_valid(form)


class VerifyPhoneNumberForUpdate(LoginRequiredMixin, FormView):
    form_class = CodeForm
    template_name = 'profile/change-number-submit.html'
    login_url = 'login'
    success_url = reverse_lazy('get_profile')

    def get_context_data(self, **kwargs):
        kwargs['phone'] = self.request.session['reset_phone']['phone']
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        typed_code = form.cleaned_data['number']
        code = self.request.session['reset_phone']['code']
        phone = self.request.session['reset_phone']['phone']
        if typed_code == code:
            try:
                user = CustomUser.objects.get(
                    phone_number=self.request.session['reset_phone'] /
                    ['old_phone']
                )
            except CustomUser.DoesNotExist:
                messages.error(self.request,
                               "User with this phone doesn't exist!")
                return render(self.request, self.template_name, {'form': form})
            else:
                user.phone_number = phone
                user.save(update_fields=['phone_number'])
                messages.success(self.request,
                                 'Phone number successfully updated.')
                return super().form_valid(form)
        messages.error(self.request, 'Code does not match up!')
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return reverse('get_profile', kwargs={'pk': self.request.user.pk})


class ProfileUpdatePassword(LoginRequiredMixin, View):
    form_class = PasswordChangeForm
    template_name = 'profile/change-password.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('get_profile', request.user.id)
        return render(request, self.template_name, {'form': form})
