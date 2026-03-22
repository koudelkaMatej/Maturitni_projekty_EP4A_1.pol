from django.urls import path
from . import views

urlpatterns = [
    path("", views.main, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('api/update_score/', views.update_score, name='update_score'),
    path('update_email/', views.update_email, name='update_email'),
]
