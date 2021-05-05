from django.urls import path
from . import views


urlpatterns = [
    # admin pages
    path('add_product/', views.AddProductView.as_view(),
         name='add_product'),
    path('delete_product/<slug:slug>/', views.DeleteProductView.as_view(),
         name='delete_product'),
    path('product_page/', views.ProductPageView.as_view(),
         name='product_page'),

    # customer pages
    path('store/', views.StoreView.as_view(),
         name='store'),
    path('cart/', views.CartView.as_view(),
         name='cart'),
    path('checkout/', views.CheckoutView.as_view(),
         name='checkout'),
    path('product_detail/<slug:slug>/', views.ProductDetailView.as_view(),
         name='product_detail'),
    path('add_to_cart/<slug:slug>/', views.AddToCartView.as_view(),
         name='add_to_cart'),
    path('remove_from_cart/<slug:slug>/', views.RemoveFromCartView.as_view(),
         name='remove_from_cart'),

    # get payment responce
    path('api/purchases/payment_response/', views.PaymentResult.as_view(),
         name='get_payment_response'),
    path('user/checkout/', views.PaymentRedirect.as_view(),
         name='payment_result'),
]
