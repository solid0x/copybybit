from django.urls import path

from . import views

urlpatterns = [
    path('api/master-traders/recent-positions', views.get_recent_positions)
]
