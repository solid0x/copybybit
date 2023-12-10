from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from bybit.utils import dummy_pos
from .models import UserProfile


def index(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        context = {'user_profile': profile}
        return render(request, 'dashboard/dashboard.html', context)
    else:
        return render(request, 'dashboard/auth.html')


def user_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    return redirect('index')


def user_register(request):
    form = UserCreationForm(request.POST)
    print(form)
    if form.is_valid():
        user = form.save()
        login(request, user)
    return redirect('index')


def user_profile(request):
    if request.method == 'POST':
        api_key = request.POST['key']
        api_secret = request.POST['secret']
        profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'api_key': '', 'api_secret': ''})
        profile.api_key = api_key
        profile.api_secret = api_secret
        profile.save()
        return JsonResponse({'status': 'ok'})
    else:
        profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={'api_key': '', 'api_secret': ''})
        return JsonResponse({'api_key': profile.api_key, 'api_secret': profile.api_secret})
