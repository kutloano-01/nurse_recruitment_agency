from rest_framework import serializers
from .models import EmployerProfile, StaffingRequest
import datetime


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'facility_name', 'facility_type', 'province', 'city',
            'address', 'contact_person', 'phone', 'created_at',
        ]

    def validate_phone(self, value):
        digits = value.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 10:
            raise serializers.ValidationError(
                'Please enter a valid phone number with at least 10 digits.'
            )
        return value

    def validate_facility_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                'Facility name must be at least 3 characters.'
            )
        return value.strip()

    def validate_address(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Please enter a valid street address.'
            )
        return value.strip()

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

    def validate_number_of_nurses(self, value):
        if value < 1:
            raise serializers.ValidationError('At least 1 nurse must be requested.')
        if value > 100:
            raise serializers.ValidationError('Cannot request more than 100 nurses at once.')
        return value

    def validate_start_date(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError('Start date cannot be in the past.')
        return value

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date cannot be before start date.'})
        return data

    def create(self, validated_data):
        employer = self.context['request'].user.employer_profile
        return StaffingRequest.objects.create(employer=employer, **validated_data)
