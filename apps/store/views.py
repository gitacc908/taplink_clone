from django.utils import timezone
from django.shortcuts import render, HttpResponse, redirect 
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .mixins import CustomerMixin
from .models import Product, Category, Order, CartProduct, Customer
from .forms import ProductMultiModelForm, ProductForm, OrderForm
from apps.store.payment.callback import result_handler
from apps.store.payment.paybox import get_url
from itertools import chain
from django.contrib import messages


class AddProductView(LoginRequiredMixin, FormView):
    template_name = 'admin_templates/add_product.html'
    login_url = 'login'
    success_url = reverse_lazy('store')
    form_class = ProductMultiModelForm

    def form_valid(self, form):
        product = form['product'].save(commit=False)
        product_image = form['product_image'].save(commit=False)
        product.owner = self.request.user
        product.save()
        product_image.product = product
        product_image.save()
        return super().form_valid(form)


class ProductDetailView(CustomerMixin, DetailView):
    model = Product
    template_name = 'detail_product.html'
    
    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])


class ProductPageView(LoginRequiredMixin, CustomerMixin, ListView):
    model = Product
    template_name = 'product_page.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super(ProductPageView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(owner=self.request.user)
        return context


class StoreView(CustomerMixin, TemplateView):
    template_name = 'store.html'

    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['products'] =  Product.objects.all()
        return context


class AddToCartView(CustomerMixin, View):

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        cart_product, created = CartProduct.objects.get_or_create(
                                                        product=product,
                                                        customer=self.customer
                                                        )
        try:
            order = Order.objects.get(customer=self.customer, status=0)
        except Order.DoesNotExist:
            order = Order.objects.create(customer=self.customer)
            order.products.add(cart_product)
            messages.info(request, 'Product was added and cart created.')
            return redirect('cart')
        else:
            if order.products.filter(product__slug=product.slug).exists():
                cart_product.quantity += 1
                cart_product.save(update_fields=['quantity'])
                messages.info(request, 'Product amount increased.')
                return redirect('cart')
            else:
                order.products.add(cart_product)
                messages.info(request, 'Product was added.')
                return redirect('cart')            


class RemoveFromCartView(CustomerMixin, View):
        
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        order_qs = Order.objects.filter(customer=self.customer, status=0)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__slug=product.slug).exists():
                cartproduct = CartProduct.objects.filter( 
                                                        product=product, 
                                                        customer=self.customer
                                                        )[0]
                cartproduct.delete()
                messages.info(request, 'Product is removed from cart!')
                return redirect('cart')
            else:
                return HttpResponse('Product is not in your cart!')
        else:
            return HttpResponse('Your cart does not exist!')


class CartView(CustomerMixin, DetailView):
    model = Order
    template_name = 'cart.html'
    
    def get_object(self):
        order = Order.objects.prefetch_related('products').get(
                                                        customer=self.customer
                                                        )
        return order


class CheckoutView(CustomerMixin, FormView):
    form_class = OrderForm
    template_name = 'checkout.html'
    success_url = reverse_lazy('store')

    def form_valid(self, form):
        order = get_object_or_404(Order, customer=self.customer)
        form.instance = order
        new_form = form.save(commit=False)
        new_form.first_name = form.cleaned_data['first_name']
        new_form.last_name = form.cleaned_data['last_name']
        new_form.phone = form.cleaned_data['phone']
        new_form.comment = form.cleaned_data['comment']
        new_form.address = form.cleaned_data['address']
        new_form.buying_type = form.cleaned_data['buying_type']
        new_form.save()
        if new_form.buying_type == 4:
            payment_res = get_url(new_form, new_form.comment, self.request)
            result_handler(payment_res)
        else:
            return HttpResponse('Our manager will call ya!:)')
        return super().form_valid(form)


class PaymentResult(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'payment_result.html')
