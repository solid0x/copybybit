from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from dashboard.models import UserProfile
from .services import TradeService
from bybit.utils import *
from dataclasses import asdict


@login_required
def place_order(request):
    profile = UserProfile.objects.get(user=request.user)
    trade_service = TradeService(profile.api_key, profile.api_secret)

    symbol = request.POST['symbol']
    side = request.POST['side']
    cost = Decimal(request.POST['cost'])
    leverage = Decimal(request.POST['leverage'])
    position = dummy_pos(symbol, side, leverage=leverage)

    trade_service.open_position(position, cost)
    return JsonResponse({'status': 'success'})


@login_required
def open_positions(request):
    profile = UserProfile.objects.get(user=request.user)
    trade_service = TradeService(profile.api_key, profile.api_secret)
    positions_info = trade_service.get_open_positions()
    return JsonResponse([asdict(pos) for pos in positions_info], safe=False)


@login_required
def close_position(request):
    profile = UserProfile.objects.get(user=request.user)
    trade_service = TradeService(profile.api_key, profile.api_secret)
    symbol = request.GET.get('symbol')
    side = request.GET.get('side')
    position = dummy_pos(symbol, side)
    trade_service.close_position(position)
    return JsonResponse({'status': 'success'})
