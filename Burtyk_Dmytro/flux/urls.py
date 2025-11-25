from django.urls import path 
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart, name="cart"),
    path("cart/checkout/", views.checkout, name="cheackout"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path("cart/delete/<int:pk>/", views.cart_delete, name='cart_delete')
]
