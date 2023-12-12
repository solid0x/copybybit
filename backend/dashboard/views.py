import logging

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse

from .models import UserProfile


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


def signin(request):
    return render(request, 'dashboard/auth.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def user_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    return redirect('dashboard')


def user_logout(request):
    logout(request)
    return redirect('login')


def user_register(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        UserProfile.objects.create(user=user, api_key='', api_secret='')
        login(request, user)
    return redirect('dashboard')


@login_required
def user_profile(request):
    if request.method == 'POST':
        try:
            api_key = request.POST['key']
            api_secret = request.POST['secret']

            profile = UserProfile.objects.get(user=request.user)
            profile.api_key = api_key
            profile.api_secret = api_secret
            profile.save()

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            logging.exception(f'Failed to update user profile: {e}')
            return JsonResponse({
                'status': 'error',
                'message': str(e),
            }, status=500)

    elif request.method == 'GET':
        profile = UserProfile.objects.get(user=request.user)
        return JsonResponse({
            'api_key': profile.api_key,
            'api_secret': profile.api_secret,
        })

    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)
