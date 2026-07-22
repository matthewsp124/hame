from django.urls import path
from hame import views

# any URLs handled here will start "www.servername.com/hame/"
app_name = 'hame'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('resources/', views.resources, name='resources'),
]