from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import UserEntry

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

REVIEW_ANSWER_CHOICES = [
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

class UserEntryForm(forms.ModelForm):
    class Meta:
        model = UserEntry
        exclude = ['user', 'location', 'created_at']  # exclude auto-filled fields
        widgets = {
            'wheelchair': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'auto_doors': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'level_floor_or_lift': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'accessible_toilet': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'parking': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'disabled_bay': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'braille_signage': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'hearing_loop': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'quiet_space': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'tactile_paving': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'nonvisual_crossing_cues': forms.Select(choices=REVIEW_ANSWER_CHOICES),
            'surface_type': forms.Select(choices=SURFACE_CHOICES),
            'gradient': forms.Select(choices=[('F', 'Flat'), ('G', 'Gentle'), ('M', 'Moderate'), ('S', 'Steep'), ('U', 'Unknown'), ('NA', 'Not applicable')]),
            'text_body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Additional comments or observations...'}),
        }
        labels = {
            'wheelchair': 'Wheelchair accessible entrance?',
            'auto_doors': 'Automatic doors?',
            'level_floor_or_lift': 'Is there level flooring? If not, is there lift access?',
            'accessible_toilet': 'Accessible toilet available?',
            'parking': 'Parking available on-site?',
            'disabled_bay': 'Disabled parking bay on-site?',
            'braille_signage': 'Braille signage available?',
            'hearing_loop': 'Hearing loop available?',
            'quiet_space': 'Quiet space available?',
            'tactile_paving': 'Tactile paving present?',
            'nonvisual_crossing_cues': 'If this location has a road crossing, are there auditory or tactile crossing safety cues?',
            'surface_type': 'Texture of the main surface?',
            'gradient': 'Gradient of the main surface?',
            'text_body': 'Anything to add? (optional)',
        }


