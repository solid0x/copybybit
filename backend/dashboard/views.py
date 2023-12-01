from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm


def index(request):
    if request.user.is_authenticated:
        return render(request, 'dashboard/dashboard.html')
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