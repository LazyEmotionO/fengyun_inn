from django.contrib import admin

from .models import Pond, SensorReading


@admin.register(Pond)
class PondAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "species", "description")
    list_filter = ("owner",)
    search_fields = ("name", "owner__username", "owner__profile__nickname")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("pond", "measured_at", "temperature", "ph", "dissolved_oxygen", "salinity")
    list_filter = ("pond",)
    date_hierarchy = "measured_at"
