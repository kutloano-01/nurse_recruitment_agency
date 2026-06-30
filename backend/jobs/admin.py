from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'facility_name', 'province', 'contract_type', 'status', 'created_at']
    list_filter = ['status', 'contract_type', 'province']
    search_fields = ['title', 'facility_name']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'job', 'status', 'applied_at']
    list_filter = ['status']
    search_fields = ['nurse__user__email', 'job__title']
