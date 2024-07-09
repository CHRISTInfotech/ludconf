from django.urls import path

from conference.views import home

urlpatterns = [
    path('',home,name='home')
]
