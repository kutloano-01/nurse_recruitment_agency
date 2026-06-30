from django.contrib import admin
from .models import EmployerProfile, StaffingRequest


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['facility_name', 'facility_type', 'province', 'contact_person']
    list_filter = ['facility_type', 'province']
    search_fields = ['facility_name', 'contact_person']


@admin.register(StaffingRequest)
class StaffingRequestAdmin(admin.ModelAdmin):
    list_display = ['employer', 'nursing_category', 'number_of_nurses', 'urgency', 'status', 'created_at']
    list_filter = ['status', 'urgency']
    search_fields = ['employer__facility_name']
