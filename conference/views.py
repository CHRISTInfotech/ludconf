from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from conference.functions import generate_otp
from conference.mails import send_otp_email
from conference.models import Conference, OTPRequest, UserDetails, ConferenceOrganisers, ConferenceDetails


# Create your views here.
def home(request):
    return render(request, 'conference/index.html')


def ludlogin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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


def ludregister(request):
    if request.method.lower() == 'post':
        email = request.POST.get('email')
        otp = generate_otp()
        ret = send_otp_email(email, otp)
        if ret:
            messages.success(request, 'Your OTP has been sent to you')
            if OTPRequest.objects.filter(email=email).exists():
                new_otp = OTPRequest.objects.get(email=email)
                new_otp.otp = otp
                new_otp.save()
            else:
                newotp = OTPRequest.objects.create(email=email, otp=otp)
                newotp.save()
            return redirect('ludregister_step_2', email)
        else:
            messages.error(request, 'unable to process your request now,\
                            please try after some time or contacting LUD Admin')
            return redirect('ludregister')
    return render(request, 'userauth/registration.html')


def ludregister_step_2(request, email):
    if OTPRequest.objects.filter(email=email).exists():
        otpRequest = OTPRequest.objects.get(email=email)
        if request.method == 'POST':
            otp = request.POST.get('otp')
            if otp == otpRequest.otp:
                messages.success(request, 'Your OTP has been been validated, please create an account')
                return redirect('ludregister_step_3', email)
            else:
                messages.error(request, 'Invalid OTP')
                return redirect('ludregister_step_3', email)
        return render(request, 'userauth/registration_step_2.html', context={'email': email, 'otpRequest': otpRequest})
    else:
        messages.error(request, 'OTP Request does not exist, please try again')
        return redirect('ludregister')


def ludregister_step_3(request, email):
    if OTPRequest.objects.filter(email=email).exists():
        if request.method == 'POST':
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            designation = request.POST.get('designation')
            organization = request.POST.get('organization')
            mobile = request.POST.get('mobile')
            password = request.POST.get('password')
            user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name,
                                            username=email)
            user.save()
            userdetails = UserDetails(user=user, gender=gender, dob=dob, designation=designation,
                                      organization=organization, mobile=mobile)
            userdetails.save()

            try:
                conferences = ConferenceOrganisers.objects.filter(mails=user.email)
                if conferences.exists():
                    user.is_staff = True
                    user.save()
                    messages.success(request, 'You are a conference organiser, your conferences are now linked')
            except:
                pass

            messages.success(request, 'Your Account has been created')
            return redirect('ludlogin')

        return render(request, 'userauth/registration_step_3.html', context={'email': email})
    else:
        messages.error(request, 'OTP Request does not exist, please try again')
        return redirect('ludregister')


def dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        active_conferences = Conference.objects.filter(is_published=True).count()
        all_conferences = Conference.objects.all().count()
        return render(request, 'siteadmin/dashboard.html',
                      context={'active_conferences': active_conferences, 'all_conferences': all_conferences})
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'organiser/dashboard.html')
    if request.user.is_authenticated:
        return render(request, 'participant/dashboard.html')
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

            if not ConferenceOrganisers.objects.filter(mails=organizer1, conference=newconference).exists():
                cof_org_1 = ConferenceOrganisers(mails=organizer1, conference=newconference, created_by=request.user)
                cof_org_1.save()
            if not ConferenceOrganisers.objects.filter(mails=organizer2, conference=newconference).exists():
                cof_org_2 = ConferenceOrganisers(mails=organizer2, conference=newconference, created_by=request.user)
                cof_org_2.save()
            if not ConferenceOrganisers.objects.filter(mails=organizer3, conference=newconference).exists():
                cof_org_3 = ConferenceOrganisers(mails=organizer3, conference=newconference, created_by=request.user)
                cof_org_3.save()

            if User.objects.filter(username=organizer1).exists():
                user = User.objects.get(username=organizer1)
                user.is_staff = True
                user.save()

            if User.objects.filter(username=organizer2).exists():
                user = User.objects.get(username=organizer2)
                user.is_staff = True
                user.save()

            if User.objects.filter(username=organizer3).exists():
                user = User.objects.get(username=organizer3)
                user.is_staff = True
                user.save()

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


def adminlistcompletedconference(request):
    if request.user.is_authenticated and request.user.is_superuser:
        conferences = Conference.objects.filter(is_published=False).order_by('-created_at')
        return render(request, 'siteadmin/listconferences.html', context={'conferences': conferences})


def adminmanageconference(request, conference_id):
    if request.user.is_authenticated and request.user.is_superuser:
        conference = Conference.objects.get(pk=conference_id)
        try:
            conference_details = ConferenceDetails.objects.get(conference_id=conference_id)
        except:
            conference_details = None
        return render(request, 'siteadmin/conference_details.html',
                      context={'conference': conference, 'conference_details': conference_details})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def adminconferencestatuschange(request, conference_id):
    if request.user.is_authenticated and request.user.is_superuser:
        conference = Conference.objects.get(pk=conference_id)
        conference.is_published = not conference.is_published
        conference.save()
        messages.success(request, 'Your conference status has been updated')
        return redirect('admin_manage_conference', conference_id)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def participatedconference(request):
    if request.user.is_authenticated:
        conferences = Conference.objects.filter(is_published=False).order_by('-created_at')
        return render(request, 'participant/listconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def registeredconference(request):
    if request.user.is_authenticated:
        conferences = Conference.objects.filter(is_published=True).order_by('-created_at')
        return render(request, 'participant/regconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def participateconference(request, conference_id):
    if request.user.is_authenticated:
        conference = Conference.objects.get(pk=conference_id)
        return render(request, 'participant/conference_participation.html', context={'conference': conference})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def stafforganisingconferenes(request):
    if request.user.is_authenticated and request.user.is_staff:
        conferences = Conference.objects.filter(is_published=True).order_by('-created_at')
        return render(request, 'organiser/newconference.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def stafforganisedconferene(request):
    if request.user.is_authenticated and request.user.is_staff:
        conferences = Conference.objects.filter(is_published=False).order_by('-created_at')
        return render(request, 'organiser/listconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')
