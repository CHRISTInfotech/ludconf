import logging
import matplotlib
matplotlib.use('Agg') 
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Conference, FeedbackSurveyResponse, ReflectionSurveyResponse
from .utils import str_to_bool, str_to_int 
from collections import Counter
import matplotlib.pyplot as plt
import io
import base64





from conference.functions import generate_otp
from conference.mails import send_otp_email
from conference.models import Conference, OTPRequest, UserDetails, ConferenceOrganisers, ConferenceDetails, \
    ConferenceRegistration
from conference.utils import export_to_excel, export_emails_for_newsletters


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
            newsletter = request.POST.get('opt_newsletter')
            if not newsletter:
                newsletter = False
            else:
                newsletter = True

            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
            else:
                user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name,
                                            username=email)
                user.save()

            if not UserDetails.objects.filter(user=user).exists():            
                userdetails = UserDetails(user=user, gender=gender, dob=dob, designation=designation,
                                      organization=organization, mobile=mobile, opt_newsletter=newsletter)
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
            org_mob_1 = request.POST.get('org_mob_1')
            org_mob_2 = request.POST.get('org_mob_2')
            org_mob_3 = request.POST.get('org_mob_3')
            newconference = Conference(title=conference_title, location=location, venue=venue, start_date=startDate,
                                       end_date=endDate, organizer1=organizer1, organizer2=organizer2,
                                       organizer3=organizer3, mobile1=org_mob_1, mobile2=org_mob_2, mobile3=org_mob_3,
                                       created_by=request.user)
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
            org_mob_1 = request.POST.get('org_mob_1')
            org_mob_2 = request.POST.get('org_mob_2')
            org_mob_3 = request.POST.get('org_mob_3')
            banner = request.FILES.get('confbanner')
            brochure = request.FILES.get('confbrochure')
            theme = request.POST.get('conftheme')
            description = request.POST.get('confdesc')
            feedback = request.POST.get('conffeedback')
            social_facebook = request.POST.get('social_facebook')
            social_insta = request.POST.get('social_insta')
            social_linkedin = request.POST.get('social_linkedin')
            social_twitter = request.POST.get('social_twitter')
            social_youtube = request.POST.get('social_youtube')

            conference.title = conference_title
            conference.location = location
            conference.venue = venue
            conference.startDate = startDate
            conference.endDate = endDate
            conference.organizer1 = organizer1
            conference.organizer2 = organizer2
            conference.organizer3 = organizer3
            conference.mobile1 = org_mob_1
            conference.mobile2 = org_mob_2
            conference.mobile3 = org_mob_3
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
                if brochure:
                    conferenceDetails.conference_brochure = brochure
                if theme:
                    conferenceDetails.conference_theme = theme
                if description:
                    conferenceDetails.conference_description = description
                if feedback:
                    conferenceDetails.conference_feedback_link = feedback
                if social_facebook != "None":
                    conferenceDetails.social_facebook = social_facebook
                if social_insta != "None":
                    conferenceDetails.social_insta = social_insta
                if social_linkedin != "None":
                    conferenceDetails.social_linkedin = social_linkedin
                if social_twitter != "None":
                    conferenceDetails.social_twitter = social_twitter
                if social_youtube != "None":
                    conferenceDetails.social_youtube = social_youtube
                conferenceDetails.save()
            else:
                conferenceDetails = ConferenceDetails(conference_id=conference.conference_id, conference_banner=banner,
                                                      conference_brochure=brochure, conference_theme=theme,
                                                      conference_description=description,
                                                      conference_feedback_link=feedback,
                                                      social_facebook=social_facebook,
                                                      social_insta=social_insta, social_linkedin=social_linkedin,
                                                      social_twitter=social_twitter, social_youtube=social_youtube)
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


@login_required(login_url='ludlogin', redirect_field_name='next')
def participateconference(request, conference_id):
    if request.user.is_authenticated:
        conference = Conference.objects.get(pk=conference_id)
        if request.method.lower() == 'post':
            interest = request.POST.get('participation')
            if ConferenceRegistration.objects.filter(conference_id=conference_id, user=request.user).exists():
                conference_reg = ConferenceRegistration.objects.get(user=request.user, conference_id=conference_id)
                conference_reg.interest = interest
                conference_reg.save()
            else:
                conferenceReg = ConferenceRegistration(interest=interest, conference_id=conference.conference_id,
                                                       user=request.user)
                conferenceReg.save()
            messages.success(request, 'You have registered for the conference')
            return redirect('registered_conference')
        try:
            conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
        except:
            conferenceDetails = None
        context = {'conference': conference, 'conferenceDetails': conferenceDetails}
        return render(request, 'conference/conference_participation.html', context=context)
    else:
        messages.error(request, 'You are not logged in')
        return redirect('ludlogin')


def conference_details(request, conference_id):
    conference = Conference.objects.get(pk=conference_id)
    try:
        conference_details = ConferenceDetails.objects.get(conference_id=conference_id)
    except:
        conference_details = None

    context = {'conference': conference, 'conference_details': conference_details}
    return render(request, 'conference/conference_details.html', context=context)


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
            brochure = request.FILES.get('confbrochure')
            theme = request.POST.get('conftheme')
            description = request.POST.get('confdesc')
            feedback = request.POST.get('conffeedback')
            social_facebook = request.POST.get('social_facebook')
            social_insta = request.POST.get('social_insta')
            social_linkedin = request.POST.get('social_linkedin')
            social_twitter = request.POST.get('social_twitter')
            social_youtube = request.POST.get('social_youtube')


            if ConferenceDetails.objects.filter(conference_id=conference.conference_id).exists():
                conferenceDetails = ConferenceDetails.objects.get(conference_id=conference.conference_id)
                if banner:
                    conferenceDetails.conference_banner = banner
                if brochure:
                    conferenceDetails.conference_brochure = brochure
                if theme:
                    conferenceDetails.conference_theme = theme
                if description:
                    conferenceDetails.conference_description = description
                if feedback:
                    conferenceDetails.conference_feedback_link = feedback
                if social_facebook != "None":
                    conferenceDetails.social_facebook = social_facebook
                if social_insta != "None":
                    conferenceDetails.social_insta = social_insta
                if social_linkedin != "None":
                    conferenceDetails.social_linkedin = social_linkedin
                if social_twitter != "None":
                    conferenceDetails.social_twitter = social_twitter
                if social_youtube != "None":
                    conferenceDetails.social_youtube = social_youtube
                conferenceDetails.save()
            else:
                conferenceDetails = ConferenceDetails(conference_id=conference.conference_id, conference_banner=banner,
                                                      conference_brochure=brochure, conference_theme=theme,
                                                      conference_description=description,
                                                      conference_feedback_link=feedback,
                                                      social_facebook=social_facebook,
                                                      social_insta=social_insta, social_linkedin=social_linkedin,
                                                      social_twitter=social_twitter, social_youtube=social_youtube)
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
        # print(queryset)
        response = export_to_excel(queryset)
        return response
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def download_emails_for_newsletter(request):
    if request.user.is_authenticated and request.user.is_staff or request.user.is_superuser:
        queryset = UserDetails.objects.filter(opt_newsletter=True).values('user__first_name',
                                                                          'user__last_name', 'user__email')
        response = export_emails_for_newsletters(queryset)
        return response
    else:
        messages.error(request, 'You are not logged in')
        return redirect('home')


def one_time_participation(request,conference_id):
    if Conference.objects.filter(pk=conference_id).exists():
        conference = Conference.objects.get(pk=conference_id)
        if request.method == "POST":
            email = request.POST['email']
            first_name = request.POST['firstname']
            last_name = request.POST['lastname']
            gender = request.POST['gender']
            dob = request.POST['dob']
            designation = request.POST['designation']
            orgnization = request.POST['organization']
            mobile = request.POST['mobile']
            newsletter = False
            
            if not User.objects.filter(email=email).exists():
                user = User.objects.create(email=email, password=mobile, first_name=first_name, last_name=last_name,
                                            username=email)
                user.save()
            else:
                user = User.objects.get(email=email)

            if not UserDetails.objects.filter(user=user).exists():
                userdetails = UserDetails(user=user, gender=gender, dob=dob, designation=designation,
                                      organization=orgnization, mobile=mobile, opt_newsletter=newsletter)
                userdetails.save()

            if ConferenceRegistration.objects.filter(conference_id=conference_id, user=user.id).exists():
                conference_reg = ConferenceRegistration.objects.get(user=user, conference_id=conference_id)
                conference_reg.interest = "Attend-Onetime"
                conference_reg.save()
            else:
                conferenceReg = ConferenceRegistration(interest="Attend-Onetime", conference_id=conference.conference_id,
                                                       user=user)
                conferenceReg.save()

            messages.success(request, 'You have registered for the conference')
            return redirect('conference_details', conference_id)
        else: 
            try:
                conference_details = ConferenceDetails.objects.get(conference=conference.pk)
            except:
                conference_details = None
            return render(request, 'conference/one_time_reg.html', context={'conference': conference, 'conference_details':conference_details})
    else:
        messages.error(request, 'Conference does not exist')
        return redirect('home')
    

def error_view_404(request, exception):
    return render(request, 'userauth/error_page.html')

def error_view_500(request):
    return render(request, 'userauth/error_page.html')

def str_to_bool(value):
    return value == 'True'

def str_to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

@login_required
def feedback_survey(request):
    conferences = Conference.objects.filter(is_published=True)
    selected_conference = None

    if request.method == 'POST':
        selected_id = request.POST.get('conference_id')
        if selected_id:
            selected_conference = get_object_or_404(Conference, conference_id=selected_id)

        if 'full_name' in request.POST:
            FeedbackSurveyResponse.objects.create(
                user=request.user,
                conference=selected_conference,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone') or None,
                age=request.POST.get('age') or None,
                gender=request.POST.get('gender') or None,
                occupation=request.POST.get('occupation'),
                occupation_other=request.POST.get('occupation_other') or None,
                location_type=request.POST.get('location_type') or None,
                first_time=str_to_bool(request.POST.get('first_time')),

                # Volunteerism & Community Engagement
                q1_volunteer=str_to_int(request.POST.get('q1_volunteer')),
                q2_belonging=str_to_int(request.POST.get('q2_belonging')),
                q3_inspiration=str_to_int(request.POST.get('q3_inspiration')),
                q4_stalls=str_to_int(request.POST.get('q4_stalls')),
                q5_reflection=str_to_int(request.POST.get('q5_reflection')),

                # Social Entrepreneurship & Community Service
                q6_initiative=str_to_int(request.POST.get('q6_initiative')),
                q7_models=str_to_int(request.POST.get('q7_models')),
                q8_motivation=str_to_int(request.POST.get('q8_motivation')),
                q9_clarity=str_to_int(request.POST.get('q9_clarity')),
                q10_insight=str_to_int(request.POST.get('q10_insight')),

                # Learning & Knowledge Sharing
                q11_concepts=str_to_int(request.POST.get('q11_concepts')),
                q12_application=str_to_int(request.POST.get('q12_application')),
                q13_expansion=str_to_int(request.POST.get('q13_expansion')),
                q14_keynotes=str_to_int(request.POST.get('q14_keynotes')),

                # Networking & Collaboration
                q15_collab=str_to_int(request.POST.get('q15_collab')),
                q16_convo=str_to_int(request.POST.get('q16_convo')),
                q17_diversity=str_to_int(request.POST.get('q17_diversity')),
                q18_community=str_to_int(request.POST.get('q18_community')),
                q19_followup=str_to_int(request.POST.get('q19_followup')),

                # Final Reflections
                followup_study=str_to_bool(request.POST.get('followup_study')) if request.POST.get('followup_study') else False,
                satisfaction=str_to_int(request.POST.get('satisfaction')),
                takeaways=request.POST.get('takeaways'),
                suggestions=request.POST.get('suggestions'),
                team_interest=str_to_bool(request.POST.get('team_interest')) if request.POST.get('team_interest') else False,
                engaging_activity=request.POST.get('engaging_activity') or None,
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect('dashboard')

    elif request.method == 'GET' and 'conference_id' in request.GET:
        selected_id = request.GET.get('conference_id')
        selected_conference = get_object_or_404(Conference, conference_id=selected_id)

    return render(request, 'forms/feedback_form.html', {
        'conferences': conferences,
        'selected_conference': selected_conference
    })

@login_required
def reflection_survey(request):
    conferences = Conference.objects.filter(is_published=True)

    selected_conference = None
    if request.method == 'POST':
        selected_id = request.POST.get('conference_id')
        if selected_id:
            selected_conference = Conference.objects.get(conference_id=selected_id)

        if 'full_name' in request.POST:
            ReflectionSurveyResponse.objects.create(
                user=request.user,
                conference=selected_conference,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                occupation=request.POST.get('occupation'),
                occupation_other=request.POST.get('occupation_other') or '',
                connect_new=request.POST.get('connect_new'),
                stayed_in_touch=request.POST.get('stayed_in_touch'),
                opportunities_found=request.POST.get('opportunities_found'),
                motivated_to_volunteer=request.POST.get('motivated_to_volunteer'),
                participated_due_to_conf=request.POST.get('participated_due_to_conf'),
                engaged_in_theme=request.POST.get('engaged_in_theme'),
                improved_knowledge=request.POST.get('improved_knowledge'),
                philosophy_applied=request.POST.get('philosophy_applied'),
                more_informed=request.POST.get('more_informed'),
                leadership_enhanced=request.POST.get('leadership_enhanced'),
                more_socially_engaged=request.POST.get('more_socially_engaged'),
                more_socially_sensitive=request.POST.get('more_socially_sensitive'),
                making_impact=request.POST.get('making_impact'),
                key_takeaway=request.POST.get('key_takeaway'),
                recommend=request.POST.get('recommend') == 'True',
                stay_involved=request.POST.get('stay_involved') == 'True',
                org_willing_to_partner=request.POST.get('org_willing_to_partner') == 'True',
            )
            messages.success(request, "Thank you for your reflection!")
            return redirect('dashboard')

    return render(request, 'forms/reflection_survey.html', {
        'conferences': conferences,
        'selected_conference': selected_conference
    })

def generate_chart(title, data_dict):
    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(data_dict.keys(), data_dict.values(), color="#4C9BE8", edgecolor='white', linewidth=0.7)

    # Rounded bars and labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=9, color='black')

    ax.set_title(title, fontsize=12, color='#004080')
    ax.set_ylabel("Responses", fontsize=10)
    ax.tick_params(axis='x', rotation=30, labelsize=9)
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=120)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    return base64.b64encode(image_png).decode("utf-8")


@login_required
def feedback_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect("home")

    responses = FeedbackSurveyResponse.objects.all().order_by("-submitted_at")
    total_responses = responses.count()

    # Define Likert/Boolean chart fields and their display titles
    chart_fields = {
        "q1_volunteer": "Interest in Volunteering",
        "q2_belonging": "Sense of Belonging",
        "q3_inspiration": "Inspired by Speakers",
        "q7_models": "Understanding New Models",
        "q11_concepts": "New Concepts or Perspectives",
        "q15_collab": "Found Collaborations",
        "followup_study": "Interest in Follow-Up Study",
        "satisfaction": "Overall Satisfaction (1–5)",
    }

    charts = []

    location_counts = Counter(res.location_type for res in responses if res.location_type)
    if location_counts:
        location_chart = generate_chart("Location of Participants", location_counts)
        charts.append({
            "title": "Location of Participants",
            "image_base64": location_chart
        })


    for field, title in chart_fields.items():
        counts = {}
        for res in responses:
            val = getattr(res, field, None)
            if isinstance(val, bool):
                key = "Yes" if val else "No"
            elif val is not None:
                key = str(val)
            else:
                continue
            counts[key] = counts.get(key, 0) + 1
        if counts:
            chart_image = generate_chart(title, counts)
            charts.append({
                "title": title,
                "image_base64": chart_image
            })

    return render(request, "forms/feedback_dashboard.html", {
        "responses": responses,
        "total_responses": total_responses,
        "charts": charts,
    })

@login_required
def reflection_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('home')

    responses = ReflectionSurveyResponse.objects.all().order_by('-submitted_at')
    total = responses.count()

    chart_fields = {
        'connect_new': 'Connected with New People',
        'stayed_in_touch': 'Stayed in Touch Post Conference',
        'opportunities_found': 'Found Collaboration Opportunities',
        'motivated_to_volunteer': 'Motivated to Volunteer',
        'participated_due_to_conf': 'Participated Because of Conference',
        'engaged_in_theme': 'Engaged in Conference Themes',
        'improved_knowledge': 'Improved Knowledge',
        'philosophy_applied': 'Conference Philosophy Still Applies',
        'more_informed': 'More Informed After Conference',
        'leadership_enhanced': 'Enhanced Leadership Skills',
        'more_socially_engaged': 'More Socially Engaged',
        'more_socially_sensitive': 'More Socially Sensitive',
        'making_impact': 'Believes Making an Impact',
        'recommend': 'Would Recommend the Conference',
        'stay_involved': 'Wants to Stay Involved',
        'org_willing_to_partner': 'Willing to Partner with LUD',
    }

    charts = []
    for field, title in chart_fields.items():
        counts = {}
        for res in responses:
            val = getattr(res, field, None)
            if isinstance(val, bool):
                key = "Yes" if val else "No"
            elif val is not None:
                key = str(val)
            else:
                continue
            counts[key] = counts.get(key, 0) + 1
        if counts:
            image = generate_chart(title, counts)
            charts.append({'title': title, 'image_base64': image})

    return render(request, 'forms/reflection_dashboard.html', {
        'responses': responses,
        'total_responses': total,
        'charts': charts
    })