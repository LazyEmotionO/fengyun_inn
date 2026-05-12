from django.contrib import admin
from .models import Event, Story, NewsItem, ContactMessage, AIoTProject

admin.site.site_header = '風雲客棧管理後台'
admin.site.site_title = '風雲客棧'
admin.site.index_title = '數位平台管理系統'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'category', 'location', 'is_featured', 'is_upcoming']
    list_filter = ['category', 'is_featured', 'date']
    search_fields = ['title', 'description']
    list_editable = ['is_featured']
    date_hierarchy = 'date'

    def is_upcoming(self, obj):
        return obj.is_upcoming()
    is_upcoming.boolean = True
    is_upcoming.short_description = '即將舉行'


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'is_featured']
    list_filter = ['is_featured']
    search_fields = ['title', 'content', 'author']
    list_editable = ['is_featured']


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'published_date']
    list_filter = ['source']
    search_fields = ['title', 'summary']
    date_hierarchy = 'published_date'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']


@admin.register(AIoTProject)
class AIoTProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'tech_stack', 'order']
    list_editable = ['order']
    search_fields = ['title', 'description']
