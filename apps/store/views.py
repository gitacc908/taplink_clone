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
from .models import (Product, Category, Order, CartProduct, ProductImage)
from .choices import STATUS_NEW, PURCHASE_BY_CARD
from .mixins import CartMixin


class AddProductView(LoginRequiredMixin, CartMixin, FormView):
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


class DeleteProductView(LoginRequiredMixin, CartMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product_page')
    login_url = 'login'
    template_name = 'admin_templates/product_confirm_delete.html'


class ProductDetailView(LoginRequiredMixin, CartMixin, DetailView):
    model = Product
    template_name = 'detail_product.html'
    login_url = 'login'

    def get_object(self):
        self.product = get_object_or_404(Product, slug=self.kwargs['slug'])
        return self.product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['images'] = ProductImage.objects.filter(product=self.product)
        return context


class ProductPageView(LoginRequiredMixin, CartMixin, ListView):
    model = Product
    template_name = 'admin_templates/product_page.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super(ProductPageView, self).get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        if search_query:
            context['products'] = (
                Product.objects.filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                ))
        else:
            context['products'] = Product.objects.filter(
                owner=self.request.user)
        return context


class StoreView(LoginRequiredMixin, CartMixin, TemplateView):
    template_name = 'store.html'
    login_url = 'login'

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


class AddToCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        cart_product, created = CartProduct.objects.get_or_create(
            product=product,
            customer=request.user
        )
        try:
            order = Order.objects.get(
                customer=request.user, status=STATUS_NEW)
        except Order.DoesNotExist:
            order = Order.objects.create(customer=request.user)
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


class RemoveFromCartView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        order_qs = Order.objects.filter(customer=request.user,
                                        status=STATUS_NEW)
        if order_qs.exists():
            order = order_qs[0]
            if order.products.filter(product__slug=product.slug).exists():
                cartproduct = CartProduct.objects.filter(
                    product=product,
                    customer=request.user
                ).first()
                cartproduct.delete()
                messages.info(request, 'Product is removed from cart!')
                return redirect('cart')
            else:
                return HttpResponse('Product is not in your cart!')
        else:
            return HttpResponse('Your cart does not exist!')


class CartView(LoginRequiredMixin, CartMixin, DetailView):
    model = Order
    template_name = 'cart.html'
    login_url = 'login'

    def get_object(self):
        order = Order.objects.prefetch_related('products').get(
            customer=self.request.user
        )
        return order


class CheckoutView(LoginRequiredMixin, CartMixin, FormView):
    form_class = OrderForm
    template_name = 'checkout.html'
    success_url = reverse_lazy('store')
    login_url = 'login'

    def form_valid(self, form):
        order = get_object_or_404(Order, customer=self.request.user)
        order.first_name = form.cleaned_data['first_name']
        order.last_name = form.cleaned_data['last_name']
        order.phone = form.cleaned_data['phone']
        order.comment = form.cleaned_data['comment']
        order.address = form.cleaned_data['address']
        order.buying_type = form.cleaned_data['buying_type']
        order.save()
        if order.buying_type == PURCHASE_BY_CARD:
            payment_url = get_url(order, self.request)
            return redirect(payment_url)
        else:
            return HttpResponse('Our manager will call ya!:)')
        return super().form_valid(form)


class PaymentRedirect(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'payment_result.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentResult, self).get_context_data(**kwargs)
        context['payment_result'] = get_payment_info(responce)
        return context
