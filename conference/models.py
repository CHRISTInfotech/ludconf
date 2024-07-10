from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Conference(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    organizer1 = models.EmailField(max_length=255)
    organizer2 = models.EmailField(max_length=255)
    organizer3 = models.EmailField(max_length=255)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title + "\t" + self.location + "\t" + self.venue