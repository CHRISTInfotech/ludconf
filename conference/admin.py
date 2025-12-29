from django.contrib import admin

from .models import (
    Conference,
    OTPRequest,
    UserDetails,
    ConferenceRegistration,
    ConferenceDetails,
    ConferenceOrganisers,
    FeedbackSurveyResponse,
    ReflectionSurveyResponse,
)

@admin.register(FeedbackSurveyResponse)
class FeedbackSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'conference', 'location_type', 'satisfaction', 'submitted_at')
    list_filter = ('conference', 'location_type', 'satisfaction', 'submitted_at')
    search_fields = ('full_name', 'email', 'phone', 'conference__title')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)


@admin.register(ReflectionSurveyResponse)
class ReflectionSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'location', 'occupation', 'recommend', 'submitted_at')
    list_filter = ('location', 'occupation', 'recommend', 'submitted_at')
    search_fields = ('full_name', 'email', 'location')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)



# Register your models here.
admin.site.register(Conference)
admin.site.register(OTPRequest)
admin.site.register(UserDetails)
admin.site.register(ConferenceOrganisers)
admin.site.register(ConferenceDetails)
admin.site.register(ConferenceRegistration)
