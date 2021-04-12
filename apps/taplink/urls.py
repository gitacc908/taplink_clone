from django.urls import path
from .views import myview

urlpatterns = [
    path('test/', myview, name='test')
]