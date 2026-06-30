from rest_framework import serializers
from .models import EmployerProfile, StaffingRequest


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'facility_name', 'facility_type', 'province', 'city',
            'address', 'contact_person', 'phone', 'created_at',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        return EmployerProfile.objects.create(user=user, **validated_data)


class StaffingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffingRequest
        fields = [
            'id', 'nursing_category', 'speciality', 'number_of_nurses',
            'shift_type', 'start_date', 'end_date', 'urgency',
            'additional_notes', 'status', 'created_at',
        ]
        read_only_fields = ['status']

    def create(self, validated_data):
        employer = self.context['request'].user.employer_profile
        return StaffingRequest.objects.create(employer=employer, **validated_data)
