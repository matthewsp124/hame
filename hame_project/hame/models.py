from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class LocationCategory(models.Model):
    name = models.CharField(max_length = 128)

    def __str__(self):
        return self.name

class Location(models.Model):
    source_choices = [('osm', 'OpenStreetMap'), ('user', 'User-added')]
    name = models.CharField(max_length = 128)
    address = models.CharField(max_length = 256)
    lat = models.FloatField()
    lng = models.FloatField()
    category = models.ForeignKey(LocationCategory, on_delete = models.SET_DEFAULT, default = "Uncategorised", null = False)
    source = models.CharField(max_length = 16, choices = source_choices, default = "osm")
    created_by = models.ForeignKey(User, on_delete = models.PROTECT, null = True)  # protect because deletion of users should be rare and handled by admin in case of vandalism
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name

class UserEntry(models.Model):
    location = models.ForeignKey(Location, on_delete = models.CASCADE, related_name = "user_entries")
    user = models.ForeignKey(User, on_delete = models.PROTECT, null = True)  # protect because deletion of users should be rare and handled by admin in case of vandalism
    text_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)