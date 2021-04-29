from django.views.generic.detail import SingleObjectMixin
from .models import Category
from .models import Product
from django.views.generic.base import View


class StoreViewMixin(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all()
        return context
