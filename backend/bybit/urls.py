from django.urls import path

from . import views

urlpatterns = [
    path('api/master-traders/recent-positions', views.recent_positions)
]