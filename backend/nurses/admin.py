from django.contrib import admin
from .models import NurseProfile, NurseDocument, NurseAvailability


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'sanc_number', 'nursing_category', 'province', 'status']
    list_filter = ['status', 'nursing_category', 'province']
    search_fields = ['user__email', 'sanc_number', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NurseDocument)
class NurseDocumentAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'document_type', 'uploaded_at', 'verified']
    list_filter = ['document_type', 'verified']
    actions = ['mark_verified']

    def mark_verified(self, request, queryset):
        queryset.update(verified=True)
    mark_verified.short_description = 'Mark selected documents as verified'


@admin.register(NurseAvailability)
class NurseAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'day', 'shift']
