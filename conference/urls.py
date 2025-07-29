from django.urls import path

from conference.views import (
    home, ludlogin, dashboard, adminconferencecreate, ludlogout, adminlistactiveconference,
    adminlistcompletedconference, ludregister, ludregister_step_2, ludregister_step_3, registeredconference,
    participateconference, participatedconference, adminmanageconference, adminconferencestatuschange,
    stafforganisingconferenes, stafforganisedconferene, deregisteredconference, conferencepass,
    staffupdateconference, download_registration_details, adminconferenceupdate, download_emails_for_newsletter,
    conference_details, one_time_participation, conference_toolkit, feedback_survey, reflection_survey,
    feedback_dashboard, reflection_dashboard
)

urlpatterns = [
    path('', home, name='home'),
    path('login', ludlogin, name='ludlogin'),
    path('logout', ludlogout, name='ludlogout'),
    path('dashboard', dashboard, name='dashboard'),
    path('ludregister', ludregister, name='ludregister'),
    path('confirm_otp/<str:email>', ludregister_step_2, name='ludregister_step_2'),
    path('create_account/<str:email>', ludregister_step_3, name='ludregister_step_3'),
    path('admin_conference_create', adminconferencecreate, name='admin_conference_create'),
    path('admin_list_active_conference', adminlistactiveconference, name='admin_list_active_conference'),
    path('admin_list_completed', adminlistcompletedconference, name='admin_list_completed'),
    path('admin_manage_conference/<str:conference_id>', adminmanageconference, name='admin_manage_conference'),
    path('admin_conference_status/<str:conference_id>', adminconferencestatuschange, name='admin_conference_status'),
    path('admin_conference_update/<str:conference_id>', adminconferenceupdate, name='admin_conference_update'),
    path('registred_conference', registeredconference, name='registered_conference'),
    path('conference_pass/<str:conference_id>', conferencepass, name='conference_pass'),
    path('conference_details/<str:conference_id>', conference_details, name='conference_details'),
    path('participate_conference/<str:conference_id>', participateconference, name='participate_conference'),
    path('participated_conference', participatedconference, name='participated_conference'),
    path('de_register_conference/<str:conference_id>', deregisteredconference, name='de_register_conference'),
    path('staff_organizing_conference', stafforganisingconferenes, name='staff_organizing_conference'),
    path('staff_organized_conference', stafforganisedconferene, name='staff_organized_conference'),
    path('staff_update_conference/<str:conference_id>', staffupdateconference, name='staff_update_conference'),
    path('download_registration_details/<str:conference_id>', download_registration_details, name='download_registration_details'),
    path('download_emails_for_newsletter', download_emails_for_newsletter, name='download_emails_for_newsletter'),
    path('one_time_registration/<str:conference_id>', one_time_participation, name='one_time_registration'),

    # Surveys 
    path('conference/', conference_toolkit, name='conference'),
    path('conference/feedback/', feedback_survey, name='conference_feedback'),
    path('conference/reflection/', reflection_survey, name='reflection_survey'),
    path('conference/feedback-dashboard/', feedback_dashboard, name='feedback_dashboard'),
    path('conference/reflection-dashboard/', reflection_dashboard, name='reflection_dashboard'),
]
