from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dataclasses import asdict

from .services import FollowService
from .utils import dummy_pos


@login_required
def recent_positions(request):
    follow_service = FollowService()
    # follow_service.check_positions()
    # recent_positions = follow_service.get_recent_positions()
    positions = [dummy_pos('BTCUSDT', 'Buy'), dummy_pos('ETHUSDT', 'Sell')]
    return JsonResponse([asdict(pos) for pos in positions], safe=False)
