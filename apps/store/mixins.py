from django.views.generic.base import View
from .models import Customer, Order
from .choices import *


class CustomerMixin(View):

    def dispatch(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except AttributeError:
            device = request.COOKIES['device']
            customer, created = Customer.objects.get_or_create(device=device)
        self.customer = customer
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(CustomerMixin, self).get_context_data(**kwargs)
        order, created = Order.objects.get_or_create(
                            customer=self.customer, status=STATUS_NEW)
        context['order'] = order
        return context
