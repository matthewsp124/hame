from django.db import models
from django.contrib.auth.models import User

class LocationCategory(models.Model):
    name = models.CharField(max_length = 128)
    osm_key = models.CharField(max_length = 64, null = True, blank = True)
    osm_value = models.CharField(max_length = 64, null = True, blank = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['osm_key', 'osm_value'], name = 'unique_osm_key_value')
        ]

    def __str__(self):
        return self.name

def get_default_category():
    category, created = LocationCategory.objects.get_or_create(
        name = 'Uncategorised',
        defaults = {'osm_key': None, 'osm_value': None}
    )
    return category.pk

class Location(models.Model):
    source_choices = [('osm', 'OpenStreetMap'), ('user', 'User-added')]
    name = models.CharField(max_length = 128)
    address = models.CharField(max_length = 256)
    lat = models.FloatField()
    lng = models.FloatField()
    category = models.ForeignKey(LocationCategory, on_delete = models.SET_DEFAULT, default = get_default_category, null = False) # TODO: get default category id
    source = models.CharField(max_length = 16, choices = source_choices, default = 'osm')
    osm_type = models.CharField(max_length = 1, null = True, blank = True)
    osm_id = models.BigIntegerField(null = True, blank = True)
    tags = models.JSONField(default = dict, blank = True)
    created_by = models.ForeignKey(User, on_delete = models.PROTECT, null = True)  # protect because deletion of users should be rare and handled by admin in case of vandalism
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['osm_type', 'osm_id'], name = 'unique_osm_type_id', 
                                    condition = models.Q(source = 'osm'))
        ]
        

    def __str__(self):
        return self.name

class UserEntry(models.Model):
    location = models.ForeignKey(Location, on_delete = models.CASCADE, related_name = 'user_entries')
    user = models.ForeignKey(User, on_delete = models.PROTECT, null = True)  # protect because deletion of users should be rare and handled by admin in case of vandalism
    text_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)