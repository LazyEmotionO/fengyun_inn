from django.urls import path

from . import views

app_name = "water"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("alerts/", views.alerts_list, name="alerts_list"),
    path("<int:pond_id>/", views.pond_detail, name="pond_detail"),
    path("<int:pond_id>/thresholds/", views.edit_thresholds, name="edit_thresholds"),
    path("<int:pond_id>/export/", views.export_csv, name="export_csv"),
]
