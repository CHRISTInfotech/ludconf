from django.contrib import admin

from conference.models import Conference, OTPRequest, UserDetails, ConferenceOrganisers, ConferenceDetails, \
    ConferenceRegistration

# Register your models here.
admin.site.register(Conference)
admin.site.register(OTPRequest)
admin.site.register(UserDetails)
admin.site.register(ConferenceOrganisers)
admin.site.register(ConferenceDetails)
admin.site.register(ConferenceRegistration)