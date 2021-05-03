from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView

from apps.store.payment.callback import result_handler
from apps.store.payment.paybox import get_url
from .forms import ProductMultiModelForm, OrderForm
from .mixins import CustomerMixin
from .models import (Product, Category, Order, CartProduct, ProductImage)
from .choices import *


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


class DeleteProductView(LoginRequiredMixin, CustomerMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product_page')
    login_url = 'login'
    template_name = 'admin_templates/product_confirm_delete.html'


class ProductDetailView(CustomerMixin, DetailView):
    model = Product
    template_name = 'detail_product.html'

    def get_object(self):
        self.product = get_object_or_404(Product, slug=self.kwargs['slug'])
        return self.product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['images'] = ProductImage.objects.filter(product=self.product)
        return context


class ProductPageView(LoginRequiredMixin, CustomerMixin, ListView):
    model = Product
    template_name = 'admin_templates/product_page.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super(ProductPageView, self).get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        if search_query:
            context['products'] = Product.objects.filter(
                Q(
                    title__icontains=search_query)
                | Q(
                    description__icontains=search_query)
            )
        else:
            context['products'] = Product.objects.filter(owner=self.request.user)
        return context


class StoreView(CustomerMixin, TemplateView):
    template_name = 'store.html'

    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        if search_query:
            context['products'] = Product.objects.filter(
                Q(title__icontains=search_query)
            )
        else:
            context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        return context


class AddToCartView(CustomerMixin, View):

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        cart_product, created = CartProduct.objects.get_or_create(
            product=product,
            customer=self.customer
        )
        try:
            order = Order.objects.get(customer=self.customer, status=STATUS_NEW)
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
        order_qs = Order.objects.filter(customer=self.customer, 
                                        status=STATUS_NEW)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__slug=product.slug).exists():
                cartproduct = CartProduct.objects.filter(
                    product=product,
                    customer=self.customer
                ).first()
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
        if new_form.buying_type == PURCHASE_BY_CARD:
            payment_url = get_url(new_form, self.request)
            return redirect(payment_url)
        else:
            return HttpResponse('Our manager will call ya!:)')
        return super().form_valid(form)


class PaymentResult(View):

    def get(self, request, *args, **kwargs):
        result_handler(responce)
        return render(request, 'payment_result.html')

class PaymentResponce(View):
    pass
