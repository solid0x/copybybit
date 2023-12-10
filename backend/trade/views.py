from django.shortcuts import render
from django.http import JsonResponse
from dashboard.models import UserProfile
from .services import TradeService
from bybit.utils import *
from dataclasses import asdict


def place_order(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)

        symbol = request.POST['symbol']
        side = request.POST['side']
        cost = Decimal(request.POST['cost'])
        leverage = Decimal(request.POST['leverage'])
        position = dummy_pos(symbol, side, leverage=leverage)

        trade_service.open_position(position, cost)
        return JsonResponse({'status': 'success'})
    else:
        return render(request, 'dashboard/auth.html')


def open_positions(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)
        positions_info = trade_service.get_open_positions()
        return JsonResponse([asdict(pos) for pos in positions_info], safe=False)
    else:
        return render(request, 'dashboard/auth.html')


def close_position(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)
        symbol = request.GET.get('symbol')
        side = request.GET.get('side')
        position = dummy_pos(symbol, side)
        trade_service.close_position(position)
        return JsonResponse({'status': 'success'})
    else:
        return render(request, 'dashboard/auth.html')