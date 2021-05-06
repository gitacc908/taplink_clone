from django.views import View
from .models import Order
from .choices import STATUS_NEW


class CartMixin(View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order, created = Order.objects.get_or_create(
            customer=self.request.user,
            status=STATUS_NEW
        )
        context['order'] = order
        return context
