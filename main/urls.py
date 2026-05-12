from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('contact/', views.contact, name='contact'),
    path('story/', views.story, name='story'),
    path('story/<int:pk>/', views.story_detail, name='story_detail'),
    path('usr/', views.usr, name='usr'),
    path('aiot/', views.aiot, name='aiot'),
    path('activities/', views.activities, name='activities'),
    path('gallery/', views.gallery, name='gallery'),
    path('ar/', views.ar, name='ar'),
]
