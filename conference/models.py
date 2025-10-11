import uuid
import logging
from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Conference(models.Model):
    conference_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    organizer1 = models.EmailField(max_length=255)
    mobile1 = models.CharField(max_length=255, blank=True, null=True)
    organizer2 = models.EmailField(max_length=255)
    mobile2 = models.CharField(max_length=255, blank=True, null=True)
    organizer3 = models.EmailField(max_length=255)
    mobile3 = models.CharField(max_length=255, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    google_maps_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title + "\t" + self.location + "\t" + self.venue


class OTPRequest(models.Model):
    email = models.EmailField(max_length=255)
    otp = models.CharField(max_length=10)

    def __str__(self):
        return self.email + "\t" + self.otp.__str__()


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    designation = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    opt_newsletter = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class ConferenceRegistration(models.Model):
    reg_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interest = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.conference.title + "\t" + self.user.username


class ConferenceDetails(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    conference_banner = models.ImageField(upload_to="banners/")
    conference_theme = models.CharField(max_length=255)
    conference_description = models.TextField()
    conference_feedback_link = models.TextField()
    conference_brochure = models.FileField(upload_to="brochure/", null=True, blank=True)
    social_insta = models.CharField(max_length=255, null=True, blank=True)
    social_twitter = models.CharField(max_length=255, null=True, blank=True)
    social_youtube = models.CharField(max_length=255, null=True, blank=True)
    social_facebook = models.CharField(max_length=255, null=True, blank=True)
    social_linkedin = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.conference.title + "\t" + self.conference.start_date.__str__()


class ConferenceOrganisers(models.Model):
    mails = models.EmailField(max_length=255)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)


SCALE_CHOICES = [(i, str(i)) for i in range(1, 6)]
OCCUPATION_CHOICES = [
    ("University/College Faculty", "University/College Faculty"),
    ("Post-secondary faculty (vocational/technical)", "Post-secondary faculty (vocational/technical)"),
    ("Student", "Student"),
    ("Social Worker", "Social Worker"),
    ("Healthcare", "Healthcare"),
    ("Corporate Professional", "Corporate Professional"),
    ("Retired Professional", "Retired Professional"),
    ("Entrepreneur", "Entrepreneur"),
    ("Other", "Other"),
]

class FeedbackSurveyResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE)

    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=100, choices=OCCUPATION_CHOICES)
    occupation_other = models.CharField(max_length=100, blank=True, null=True)
    location_type = models.CharField(max_length=50, blank=True, null=True)
    first_time = models.BooleanField(default=False)

    # Volunteerism & Community Engagement (Q9)
    q9_1 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q9_2 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q9_3 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q9_4 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q9_5 = models.IntegerField(choices=SCALE_CHOICES, default=3)

    # Social Entrepreneurship & Community Service (Q10)
    q10_1 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q10_2 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q10_3 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q10_4 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q10_5 = models.IntegerField(choices=SCALE_CHOICES, default=3)

    # Learning & Knowledge Sharing (Q11)
    q11_1 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q11_2 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q11_3 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q11_4 = models.IntegerField(choices=SCALE_CHOICES, default=3)

    # Networking & Collaborations (Q12)
    q12_1 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q12_2 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q12_3 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q12_4 = models.IntegerField(choices=SCALE_CHOICES, default=3)
    q12_5 = models.IntegerField(choices=SCALE_CHOICES, default=3)

    # Final Reflection Questions
    followup_study = models.BooleanField(default=False)
    satisfaction = models.IntegerField(choices=SCALE_CHOICES, default=3)
    takeaways = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    team_interest = models.BooleanField(default=False)
    engaging_activity = models.CharField(max_length=255, blank=True, null=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Feedback Survey Response'
        verbose_name_plural = 'Feedback Survey Responses'

    def __str__(self):
        return f'{self.full_name or "Anonymous"} - {self.conference}'


class ReflectionSurveyResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conference = models.ForeignKey('Conference', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    occupation = models.CharField(max_length=50, choices=OCCUPATION_CHOICES)
    occupation_other = models.CharField(max_length=255, blank=True, null=True)
    
    # Survey Responses
    connect_new = models.IntegerField(choices=SCALE_CHOICES)
    stayed_in_touch = models.IntegerField(choices=SCALE_CHOICES)
    opportunities_found = models.IntegerField(choices=SCALE_CHOICES)
    motivated_to_volunteer = models.IntegerField(choices=SCALE_CHOICES)
    participated_due_to_conf = models.IntegerField(choices=SCALE_CHOICES)
    engaged_in_theme = models.IntegerField(choices=SCALE_CHOICES)
    improved_knowledge = models.IntegerField(choices=SCALE_CHOICES)
    philosophy_applied = models.IntegerField(choices=SCALE_CHOICES)
    more_informed = models.IntegerField(choices=SCALE_CHOICES)
    leadership_enhanced = models.IntegerField(choices=SCALE_CHOICES)
    more_socially_engaged = models.IntegerField(choices=SCALE_CHOICES)
    more_socially_sensitive = models.IntegerField(choices=SCALE_CHOICES)
    making_impact = models.IntegerField(choices=SCALE_CHOICES)
    
    # Final responses
    key_takeaway = models.TextField()
    recommend = models.BooleanField()
    stay_involved = models.BooleanField()
    org_willing_to_partner = models.BooleanField()

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Reflection Survey Response'
        verbose_name_plural = 'Reflection Survey Responses'
