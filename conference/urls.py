from django.urls import path

from conference.views import home, ludlogin, dashboard, adminconferencecreate, ludlogout, adminlistactiveconference, \
    adminlistcompletedconference

urlpatterns = [
    path('', home, name='home'),
    path('login', ludlogin, name='ludlogin'),
    path('logout', ludlogout, name='ludlogout'),
    path('dashboard', dashboard, name='dashboard'),
    path('admin_conference_create', adminconferencecreate, name='admin_conference_create'),
    path('admin_list_active_conference', adminlistactiveconference, name='admin_list_active_conference'),
    path('admin_list_completed', adminlistcompletedconference, name='admin_list_completed'),
]
