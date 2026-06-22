from django.urls import path

from . import views

app_name = "comments"

urlpatterns = [
    path("<str:board>/add/", views.add_comment, name="add_comment"),
]
