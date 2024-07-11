from django.urls import path

from conference.views import home, ludlogin, dashboard, adminconferencecreate, ludlogout, adminlistactiveconference, \
    adminlistcompletedconference, ludregister, ludregister_step_2, ludregister_step_3, registeredconference, \
    participateconference, participatedconference, adminmanageconference, adminconferencestatuschange, \
    stafforganisingconferenes, stafforganisedconferene

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
    path('registred_conference', registeredconference, name='registered_conference'),
    path('participated_conference', participatedconference, name='participated_conference'),

    path('staff_organizing_conference', stafforganisingconferenes, name='staff_organizing_conference'),
    path('staff_organized_conference', stafforganisedconferene, name='staff_organized_conference'),

]
