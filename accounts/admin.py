from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = UserAdmin.list_display + ("nickname", "ar_score")

    def nickname(self, obj):
        return obj.profile.nickname

    def ar_score(self, obj):
        return obj.profile.ar_score

    nickname.short_description = "暱稱"
    ar_score.short_description = "AR 累積分數"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("nickname", "user", "ar_score")
    list_editable = ("ar_score",)
    search_fields = ("nickname", "user__username")
