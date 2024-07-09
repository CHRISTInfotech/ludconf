from django.urls import path

from conference.views import home, ludlogin, admindashboard, adminconferencecreate, ludlogout

urlpatterns = [
    path('',home,name='home'),
    path('login',ludlogin,name='ludlogin'),
    path('logout',ludlogout,name='ludlogout'),
    path('admin_dashboard',admindashboard,name='admin_dashboard'),
    path('admin_conference_create',adminconferencecreate,name='admin_conference_create'),
]
