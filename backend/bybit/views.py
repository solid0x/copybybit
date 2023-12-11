import logging

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from dataclasses import asdict

from .services import FollowService


@login_required
def get_recent_positions(request):
    try:
        follow_service = FollowService()
        follow_service.check_positions()
        positions = follow_service.get_recent_positions()
        return JsonResponse([asdict(pos) for pos in positions], safe=False)
    except Exception as e:
        logging.exception(f'Failed to get recent positions: {e}')
        return JsonResponse({
            'status': 'error',
            'message': str(e),
        }, status=500)
