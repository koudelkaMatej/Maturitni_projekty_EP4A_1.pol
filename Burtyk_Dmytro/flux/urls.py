from django.urls import path 
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart, name="cart"),
    path("cart/cheackout/", views.cheackout, name="cheackout"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
]
