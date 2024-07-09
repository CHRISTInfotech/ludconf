from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect


# Create your views here.
def home(request):
    return render(request,'conference/index.html')

def ludlogin(request):
    if request.method.lower() == 'post':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('ludlogin')
    else:
        return render(request,'userauth/login.html')


def ludlogout(request):
    if request.user.is_authenticated:
        logout(request.user)
    return redirect('home')

def admindashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request,'siteadmin/dashboard.html')
    else:
        return redirect('home')


def adminconferencecreate(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request,'siteadmin/newconference.html')
    else:
        return redirect('home')