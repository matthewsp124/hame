from django.urls import path
from django.contrib.auth import views as auth_views

from hame import views

# any URLs handled here will start "www.servername.com/hame/"
app_name = 'hame'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('resources/', views.resources, name='resources'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='hame/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('reviews/<int:entry_id>/delete/', views.delete_review, name='delete_review'),
    path('locations/<int:location_id>/reviews/', views.location_reviews, name='location_reviews'),
    path('locations/<int:location_id>/reviews/add', views.add_review, name='add_review'),
]