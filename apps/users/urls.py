from django.urls import path
from django.views.generic import TemplateView
from .views import ( GetNumber, VerifyCodeView, SignUpView, 
                    GetPhoneNumber, VerifyPhoneNumber, 
                     ResetPasswordView, GetProfile, LoginView, GetPhoneForUpdate, 
                    VerifyPhoneNumberForUpdate, ProfileUpdatePassword
                    )


urlpatterns = [
    # registration 
    path('signup/get_number/', GetNumber.as_view(), name='get_number'),
    path('signup/verify/', VerifyCodeView.as_view(), name='verify_view'),
    path('signup/register/', SignUpView.as_view(), name='signup'),

    # resetpassword
    path('reset/get_phone_number/', GetPhoneNumber.as_view(), 
                                                    name='get_phone_number'),
    path('reset/verify_phone_number/', VerifyPhoneNumber.as_view(), 
                                                    name='verify_phone_number'),
    path('reset/reset_password/', ResetPasswordView.as_view(), 
                                                        name='reset_password'),
    
    # custom authentication
    path('users/login/', LoginView.as_view(), name='login'),

    # profile 
    path('profile/<int:pk>/', GetProfile.as_view(), name='get_profile'),
    path('profile/get_phone_number/', GetPhoneForUpdate.as_view(), 
                                                    name='get_phone_for_update'),
    path('profile/verify_phone_number/', VerifyPhoneNumberForUpdate.as_view(), 
                                                name='verify_phone_for_update'),
    path('profile/update_password/', ProfileUpdatePassword.as_view(), 
                                                        name='update_password'),
]
