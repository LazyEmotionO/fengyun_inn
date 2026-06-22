from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("board", "user", "text", "created_at")
    list_filter = ("board",)
    search_fields = ("text", "user__username", "user__profile__nickname")
    date_hierarchy = "created_at"
