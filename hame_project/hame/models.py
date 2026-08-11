from django.db import models
from django.contrib.auth.models import User

class LocationCategoryKey(models.Model):
    osm_key = models.CharField(max_length = 64, unique = True)

    def __str__(self):
        return self.osm_key

class LocationCategory(models.Model):
    key = models.ForeignKey(LocationCategoryKey, on_delete = models.SET_NULL, null = True, blank = False)
    osm_value = models.CharField(max_length = 64, null = True, blank = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['key', 'osm_value'], name = 'unique_osm_key_value')
        ]

    def __str__(self):
        return f"{self.key.osm_key}={self.osm_value}" 

class Location(models.Model):
    name = models.CharField(max_length = 128, null = True)
    address = models.CharField(max_length = 256, blank = True)
    lat = models.FloatField()
    lng = models.FloatField()
    categories = models.ManyToManyField(LocationCategory, blank = False)
    osm_type = models.CharField(max_length = 1, null = True, blank = True)  # currently treating all locations as nodes, but node and way IDs can overlap 
    osm_id = models.BigIntegerField(null = True, blank = True)
    tags = models.JSONField(default = dict, blank = True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['osm_type', 'osm_id'], name = 'unique_osm_type_id')
        ]

    def __str__(self):
        return f"{self.osm_id} - {self.name or self.address} ({self.lat}, {self.lng})"


ANSWER_CHOICES = [
    ('Y', 'Yes'),
    ('N', 'No'),
    ('U', 'Unknown'),
    ('NA', 'Not Applicable'),
]

SURFACE_CHOICES = [
    ('P', 'Paved/smooth'),
    ('C', 'Cobblestone'),
    ('G', 'Gravel'),
    ('S', 'Sand'),
    ('B', 'Bumpy/uneven'),
    ('U', 'Unknown'),
    ('NA', 'Not applicable'),
]

class UserEntry(models.Model):
    location = models.ForeignKey(Location, on_delete = models.CASCADE, related_name = 'user_entries')
    user = models.ForeignKey(User, on_delete = models.PROTECT, null = True)  # protect because deletion of users should be rare and handled by admin in case of vandalism
    wheelchair = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    auto_doors = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    level_floor_or_lift = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    accessible_toilet = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    parking = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    disabled_bay = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    braille_signage = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    hearing_loop = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    quiet_space = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    tactile_paving = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    nonvisual_crossing_cues = models.CharField(max_length = 2, choices = ANSWER_CHOICES, default = 'U', null = False, blank = False)
    surface_type = models.CharField(max_length = 2, choices = SURFACE_CHOICES, default = 'U', null = False, blank = False)
    gradient = models.CharField(max_length = 2, choices = [('F', 'Flat'), ('G', 'Gentle'), ('M', 'Moderate'), ('S', 'Steep'), ('U', 'Unknown'), ('NA', 'Not applicable')], default = 'U', null = False, blank = False)
    text_body = models.TextField(blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f"Entry by {self.user.username} for {self.location} ({self.created_at:%Y-%m-%d %H:%M:%S})"