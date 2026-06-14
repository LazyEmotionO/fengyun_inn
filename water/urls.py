from django.urls import path

from . import views

app_name = "water"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<int:pond_id>/", views.pond_detail, name="pond_detail"),
]
