from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect

from conference.functions import generate_otp
from conference.mails import send_otp_email
from conference.models import Conference, OTPRequest, UserDetails, ConferenceOrganisers, ConferenceDetails, \
    ConferenceRegistration
from conference.utils import export_to_excel


# Create your views here.
def home(request):
    conferences = Conference.objects.filter(is_published=True)
    conferenceDetails = ConferenceDetails.objects.filter(conference_id__in=conferences)
    context = {'conferences': conferences, 'conference_details': conferenceDetails}
    return render(request, 'conference/index.html', context=context)


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
        registrations = Conference.objects.annotate(registration_count=Count("conferenceregistration")).values("title",
                                                                                                               "registration_count",
                                                                                                               "is_published",
                                                                                                               "conference_id")
        context = {'active_conferences': active_conferences, 'all_conferences': all_conferences,
                   'registrations': registrations}
        return render(request, 'siteadmin/dashboard.html', context=context)
    if request.user.is_authenticated and request.user.is_staff:
        registeredconference = ConferenceRegistration.objects.filter(user=request.user).values('conference_id')
        conferences = Conference.objects.exclude(conference_id__in=registeredconference).exclude(is_published=False)
        conferenceDetails = ConferenceDetails.objects.filter(conference_id__in=conferences)
        context = {'conferences': conferences, 'conference_details': conferenceDetails}
        return render(request, 'organiser/dashboard.html', context=context)
    if request.user.is_authenticated:
        registeredconference = ConferenceRegistration.objects.filter(user=request.user).values('conference_id')
        conferences = Conference.objects.exclude(conference_id__in=registeredconference).exclude(is_published=False)
        conferenceDetails = ConferenceDetails.objects.filter(conference_id__in=conferences)
        context = {
            'conferences': conferences,
            'registeredconference': registeredconference,
            'conference_details': conferenceDetails
        }
        return render(request, 'participant/dashboard.html', context=context)
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

        try:
            participant_count = ConferenceRegistration.objects.filter(conference_id=conference.conference_id).count()
        except:
            participant_count = 0

        context = {'conference': conference, 'conference_details': conference_details,
                   'participant_count': participant_count}
        return render(request, 'siteadmin/conference_details.html', context=context)
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


def adminconferenceupdate(request, conference_id):
    if request.user.is_authenticated and request.user.is_superuser:
        conference = Conference.objects.get(pk=conference_id)

        if request.method.lower() == 'post':
            conference_title = request.POST.get('conferenceHeading')
            location = request.POST.get('location')
            venue = request.POST.get('venue')
            startDate = request.POST.get('fromdate')
            endDate = request.POST.get('enddate')
            organizer1 = request.POST.get('org1')
            organizer2 = request.POST.get('org2')
            organizer3 = request.POST.get('org3')
            banner = request.FILES.get('confbanner')
            theme = request.POST.get('conftheme')
            description = request.POST.get('confdesc')
            feedback = request.POST.get('conffeedback')

            conference.title = conference_title
            conference.location = location
            conference.venue = venue
            conference.startDate = startDate
            conference.endDate = endDate
            conference.organizer1 = organizer1
            conference.organizer2 = organizer2
            conference.organizer3 = organizer3
            conference.save()

            if not ConferenceOrganisers.objects.filter(mails=organizer1, conference=conference).exists():
                cof_org_1 = ConferenceOrganisers(mails=organizer1, conference=conference, created_by=request.user)
                cof_org_1.save()
            if not ConferenceOrganisers.objects.filter(mails=organizer2, conference=conference).exists():
                cof_org_2 = ConferenceOrganisers(mails=organizer2, conference=conference, created_by=request.user)
                cof_org_2.save()
            if not ConferenceOrganisers.objects.filter(mails=organizer3, conference=conference).exists():
                cof_org_3 = ConferenceOrganisers(mails=organizer3, conference=conference, created_by=request.user)
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

            if ConferenceDetails.objects.filter(conference_id=conference.conference_id).exists():
                conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
                if banner:
                    conferenceDetails.conference_banner = banner
                if theme:
                    conferenceDetails.conference_theme = theme
                if description:
                    conferenceDetails.conference_description = description
                if feedback:
                    conferenceDetails.conference_feedback_link = feedback
                conferenceDetails.save()
            else:
                conferenceDetails = ConferenceDetails(conference_id=conference.conference_id, conference_banner=banner,
                                                      conference_theme=theme, conference_description=description,
                                                      conference_feedback_link=feedback)
                conferenceDetails.save()

            messages.success(request, 'Your conference has been updated')
            return redirect('admin_conference_update', conference_id)

        try:
            conference_details = ConferenceDetails.objects.get(conference_id=conference_id)
        except:
            conference_details = None

        try:
            participant_count = ConferenceRegistration.objects.filter(conference_id=conference.conference_id).count()
        except:
            participant_count = 0

        context = {'conference': conference, 'conference_details': conference_details,
                   'participant_count': participant_count}

        return render(request, 'siteadmin/updateconference.html', context=context)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def participatedconference(request):
    if request.user.is_authenticated:
        registeredconference = ConferenceRegistration.objects.filter(user=request.user).values('conference_id')
        conferences = Conference.objects.filter(conference_id__in=registeredconference).exclude(is_published=True)
        return render(request, 'participant/listconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def registeredconference(request):
    if request.user.is_authenticated:
        registeredconference = ConferenceRegistration.objects.filter(user=request.user).values('conference_id')
        conferences = Conference.objects.filter(conference_id__in=registeredconference).exclude(is_published=False)
        return render(request, 'participant/regconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def deregisteredconference(request, conference_id):
    if request.user.is_authenticated:
        registeredconference = ConferenceRegistration.objects.get(user=request.user, conference_id=conference_id)
        registeredconference.delete()
        messages.success(request, 'Your conference registration has been deleted')
        return redirect('dashboard')
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


@login_required(login_url='ludlogin')
def participateconference(request, conference_id):
    if request.user.is_authenticated:
        conference = Conference.objects.get(pk=conference_id)
        if request.method.lower() == 'post':
            interest = request.POST.get('participation')
            conferenceReg = ConferenceRegistration(interest=interest, conference_id=conference.conference_id,
                                                   user=request.user)
            conferenceReg.save()
            messages.success(request, 'You have registered for the conference')
            return redirect('registered_conference')
        return render(request, 'conference/conference_participation.html', context={'conference': conference})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def conferencepass(request, conference_id):
    if request.user.is_authenticated:
        conference = Conference.objects.get(pk=conference_id)
        conferenceRegistration = ConferenceRegistration.objects.get(user=request.user,
                                                                    conference_id=conference.conference_id)
        try:
            conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
        except:
            conferenceDetails = None
        context = {'conference': conference, 'conferenceRegistration': conferenceRegistration,
                   'conferenceDetails': conferenceDetails}
        return render(request, 'conference/conference_pass.html', context=context)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def stafforganisingconferenes(request):
    if request.user.is_authenticated and request.user.is_staff:
        organisingConference = ConferenceOrganisers.objects.filter(mails=request.user.email).values('conference_id')
        conferences = Conference.objects.filter(is_published=True, conference_id__in=organisingConference).order_by(
            '-created_at')
        return render(request, 'organiser/newconference.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def stafforganisedconferene(request):
    if request.user.is_authenticated and request.user.is_staff:
        organisingConference = ConferenceOrganisers.objects.filter(mails=request.user.email).values('conference_id')
        conferences = Conference.objects.filter(is_published=False, conference_id__in=organisingConference).order_by(
            '-created_at')
        return render(request, 'organiser/listconferences.html', context={'conferences': conferences})
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def staffupdateconference(request, conference_id):
    if request.user.is_authenticated and request.user.is_staff:
        conference = Conference.objects.get(pk=conference_id)
        if request.method.lower() == "post":
            banner = request.FILES.get('confbanner')
            theme = request.POST.get('conftheme')
            description = request.POST.get('confdesc')
            feedback = request.POST.get('conffeedback')

            if ConferenceDetails.objects.filter(conference_id=conference.conference_id).exists():
                conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
                if banner:
                    conferenceDetails.conference_banner = banner
                if theme:
                    conferenceDetails.conference_theme = theme
                if description:
                    conferenceDetails.conference_description = description
                if feedback:
                    conferenceDetails.conference_feedback_link = feedback
                conferenceDetails.save()
            else:
                conferenceDetails = ConferenceDetails(conference_id=conference.conference_id, conference_banner=banner,
                                                      conference_theme=theme, conference_description=description,
                                                      conference_feedback_link=feedback)
                conferenceDetails.save()

            messages.success(request, 'Your conference details has been updated')
            return redirect('staff_update_conference', conference_id)
        try:
            conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
        except:
            conferenceDetails = None
        context = {
            'conference': conference,
            'conferenceDetails': conferenceDetails
        }
        return render(request, 'organiser/manage_conference.html', context)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def download_registration_details(request, conference_id):
    if request.user.is_authenticated and request.user.is_staff or request.user.is_superuser:
        queryset = ConferenceRegistration.objects.filter(conference_id=conference_id).values('registration_date',
                                                                                             'interest',
                                                                                             'user__first_name',
                                                                                             'user__last_name',
                                                                                             'user__email',
                                                                                             'user__userdetails__mobile',
                                                                                             'user__userdetails__gender',
                                                                                             'user__userdetails__dob',
                                                                                             'user__userdetails__designation',
                                                                                             'user__userdetails__organization')
        print(queryset)
        response = export_to_excel(queryset)
        return response
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')
