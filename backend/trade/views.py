import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from dataclasses import asdict

from dashboard.models import UserProfile
from bybit.utils import *
from .services import TradeService


@login_required
def place_order(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)

        symbol = request.POST['symbol']
        side = request.POST['side']
        cost = Decimal(request.POST['cost'])
        leverage = Decimal(request.POST['leverage'])
        position = dummy_pos(symbol, side, leverage=leverage)

        trade_service.open_position(position, cost)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logging.exception(f'Failed to open position: {e}')
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@login_required
def get_open_positions(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)
        positions_info = trade_service.get_open_positions()
        return JsonResponse([asdict(pos) for pos in positions_info], safe=False)
    except Exception as e:
        logging.exception(f'Failed to get open positions: {e}')
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)


@login_required
def close_position(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        trade_service = TradeService(profile.api_key, profile.api_secret)
        symbol = request.GET.get('symbol')
        side = request.GET.get('side')
        position = dummy_pos(symbol, side)
        trade_service.close_position(position)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logging.exception(f'Failed to close position: {e}')
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)
