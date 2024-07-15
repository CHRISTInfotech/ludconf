import uuid
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