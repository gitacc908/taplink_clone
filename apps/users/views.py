import json
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect

from .forms import (
    NumberForm, CodeForm, CustomUserCreationForm, 
    SetPasswordForm, CustomUserChangeForm
)

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


class GetNumber(FormView):
    template_name = 'registration/registration-number.html'
    form_class = NumberForm
    success_url = reverse_lazy('verify_view')

    def form_valid(self, form):
        phone = str(form.cleaned_data['phone'])
        try:
            CustomUser.objects.get(phone_number=phone)
            return HttpResponse('This phone is already registered!')
        except CustomUser.DoesNotExist:
            new_user = {
                'code': code_generate(),
                'phone': phone
            }
            send_sms(new_user['code'],new_user['phone'])
            self.request.session['data'] = new_user 
            return super().form_valid(form)


class VerifyCodeView(View):
    form_class = CodeForm
    template_name = 'registration/registration-submit.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'phone': request.session['data']['phone']})   

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            typed_code = form.cleaned_data.get('number')
            code = request.session['data']['code']
            if code == typed_code:
                return redirect('signup')
            else:
                return HttpResponse("Code doesn't match up!")
        return render(request, self.template_name, {'form':form})


class SignUpView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('index_page')

    def form_valid(self, form):
        phone_number = self.request.session['data']['phone']
        user = form.save(commit=False)
        user.phone_number = phone_number
        user.is_active = True
        user.save()
        return super().form_valid(form)


class GetPhoneNumber(FormView):
    form_class = NumberForm
    template_name = 'resetpassword/change_password_with_number.html'
    success_url = reverse_lazy('verify_phone_number')

    def form_valid(self,form):
        phone = str(form.cleaned_data.get('phone'))
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except CustomUser.DoesNotExist:
            return HttpResponse('User with this phone does not exist!')
        else:
            reset = {
                'code': code_generate(),
                'phone': phone
            }
            send_sms(code, user.phone_number)
            self.request.session['reset_data'] = reset
            return super().form_valid(form)


class VerifyPhoneNumber(View):
    form_class = CodeForm
    template_name = 'resetpassword/change_password_submit.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            typed_code = form.cleaned_data.get('number')
            code = request.session['reset_data']['code']
            if typed_code == code:
                return redirect('reset_password')
        return render(request, self.template_name, {'form':form})


class ResetPasswordView(View):
    form_class = SetPasswordForm
    template_name = 'resetpassword/change_password.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = get_object_or_404(CustomUser, phone_number=request.session['reset_data']['phone'])
            password = form.cleaned_data['new_password1']
            user.password = make_password(password)
            user.save(update_fields=['password'])
            # make user login after password update
            return redirect('index_page')
        return render(request, self.template_name, {'form':form})


class GetProfile(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'profile/edit-profile.html'
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        form = CustomUserChangeForm(request.POST)          
        if form.is_valid():
            new_form = form.instance.user = request.user      
            new_form.save()
            return redirect('get_profile', request.user.id)
        return render(request, self.template_name, {'form': form})


class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('index_page')

    def form_valid(self,form):
        form = self.form_class(self.request.POST)
        username = self.request.POST['username']
        password = self.request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            return super().form_valid(form)
        return render(request, 'registration/login.html', {'form': form})


class GetPhoneForUpdate(LoginRequiredMixin, FormView):
    form_class = NumberForm
    template_name = 'profile/change-number.html'
    success_url = reverse_lazy('verify_phone_for_update')
    login_url = 'login'
    
    def form_valid(self, form):
        phone = str(form.cleaned_data.get('phone'))
        if CustomUser.objects.filter(phone_number=phone).exists():
            return HttpResponse('This phone number already exists!')
        reset_phone = {
            'code': code_generate(),
            'phone': phone,
            'old_phone': str(self.request.user.phone_number)
        }
        send_sms(code, phone)
        self.request.session['reset_phone'] = reset_phone
        return super().form_valid(form)


class VerifyPhoneNumberForUpdate(View):
    form_class = CodeForm
    template_name = 'profile/change-number-submit.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, 
                    {'form': form, 
                    'phone': self.request.session['reset_phone']['phone']})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            typed_code = form.cleaned_data.get('number')
            code = request.session['reset_phone']['code']
            phone = request.session['reset_phone']['phone']
            if typed_code == code:
                try:
                    user = CustomUser.objects.get(
                        phone_number=request.session['reset_phone']['old_phone']
                    )
                except CustomUser.DoesNotExist:
                    return HttpResponse("User with this phone doesn't exist!")
                else:
                    user.phone_number = phone
                    user.save(update_fields=['phone_number'])
                    return redirect('get_profile', request.user.id)
        return render(request, self.template_name, {'form':form})


class ProfileUpdatePassord(View):
    form_class = PasswordChangeForm
    template_name = 'profile/change-password.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form':form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('get_profile', request.user.id)
        return render(request, self.template_name, {'form':form})


class ProfileUpdateView(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            data = json.load(request)
            user = request.user
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            user.save(update_fields=['first_name', 'last_name'])
            return JsonResponse({"user_update": True}, status=200)
