from django.views.generic.base import View
from .models import Customer


class CustomerMixin(View):

    def dispatch(self, request, *args, **kwargs):
        try:
            customer = request.user.customer
        except AttributeError:
            device = request.COOKIES['device']
            customer, created = Customer.objects.get_or_create(device=device)
        self.customer = customer
        return super().dispatch(request, *args, **kwargs)
