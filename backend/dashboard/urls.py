from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.signin, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('api/logout', views.user_logout),
    path('api/login', views.user_login),
    path('api/register', views.user_register),
    path('api/user/profile', views.user_profile)
]
