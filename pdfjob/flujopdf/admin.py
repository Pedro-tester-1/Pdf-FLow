from django.contrib import admin
from .models import Job, Page


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'state', 'closed', 'get_time_open')
    list_filter = ('state', 'date')
    search_fields = ('name',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'state', 'job', 'user')
    list_filter = ('state', 'date', 'job')
    search_fields = ('name',)
