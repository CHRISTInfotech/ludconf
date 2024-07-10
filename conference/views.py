from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect

from conference.models import Conference


# Create your views here.
def home(request):
    return render(request, 'conference/index.html')


def ludlogin(request):
    if request.method.lower() == 'post':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('ludlogin')
    else:
        return render(request, 'userauth/login.html')


def ludlogout(request):
    if request.user.is_authenticated:
        messages.success(request, 'You are now logged out')
        logout(request)
    return redirect('home')


def dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        active_conferences = Conference.objects.filter(is_published=True).count()
        all_conferences = Conference.objects.all().count()
        return render(request, 'siteadmin/dashboard.html',context={'active_conferences': active_conferences, 'all_conferences': all_conferences})
    if request.user.is_authenticated and request.user.is_staff:
        pass
    if request.user.is_authenticated:
        pass
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def adminconferencecreate(request):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method.lower() == 'post':
            conference_title = request.POST.get('conferenceHeading')
            location = request.POST.get('location')
            venue = request.POST.get('venue')
            startDate = request.POST.get('fromdate')
            endDate = request.POST.get('enddate')
            organizer1 = request.POST.get('org1')
            organizer2 = request.POST.get('org2')
            organizer3 = request.POST.get('org3')
            newconference = Conference(title=conference_title, location=location, venue=venue, start_date=startDate,
                                       end_date=endDate, organizer1=organizer1, organizer2=organizer2,
                                       organizer3=organizer3, created_by=request.user)
            newconference.save()
            messages.success(request, 'Your conference has been created!')
            return redirect('admin_list_active_conference')
        return render(request, 'siteadmin/newconference.html')
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def adminlistactiveconference(request):
    if request.user.is_authenticated and request.user.is_superuser:
        conferences = Conference.objects.filter(is_published=True).order_by('-created_at')
        return render(request, 'siteadmin/activeconference.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def manageconference(request,conference_id):
    if request.user.is_authenticated and request.user.is_superuser:
        conference = Conference.objects.get(pk=conference_id)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')