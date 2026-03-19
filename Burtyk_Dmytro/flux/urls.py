from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("cart/", views.cart, name="cart"),
    path("cart/checkout/", views.checkout, name="checkout"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path("cart/delete/<int:pk>/", views.cart_delete, name='cart_delete'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='flux/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('account/', views.my_account, name='my_account'),
    path('download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('contact/', views.contact, name='contact'),
    path('about_us/', views.about, name='about'),
    path('presentation/', views.presentation, name='presentation'),
]