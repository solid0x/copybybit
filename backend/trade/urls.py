from django.urls import path

from . import views

urlpatterns = [
    path('api/user/orders', views.place_order),
    path('api/user/positions', views.open_positions),
    path('api/user/positions/close', views.close_position),
]
