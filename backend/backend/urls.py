from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('dashboard.urls')),
    path('', include('bybit.urls')),
    path('', include('trade.urls')),
    path('admin/', admin.site.urls),
]
