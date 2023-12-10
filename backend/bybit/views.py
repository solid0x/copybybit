from django.http import JsonResponse
from django.shortcuts import render
from dataclasses import asdict

from .services import FollowService
from .utils import dummy_pos


def recent_positions(request):
    if request.user.is_authenticated:
        follow_service = FollowService()
        # follow_service.check_positions()
        # recent_positions = follow_service.get_recent_positions()
        recent_positions = [dummy_pos('BTCUSDT', 'Buy'), dummy_pos('ETHUSDT', 'Sell')]
        return JsonResponse([asdict(pos) for pos in recent_positions], safe=False)
    else:
        return render(request, 'dashboard/auth.html')
