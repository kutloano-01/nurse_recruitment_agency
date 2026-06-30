from rest_framework import serializers
from .models import Job, JobApplication


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'facility_name', 'province', 'city',
            'contract_type', 'nursing_category', 'salary_display',
            'description', 'requirements', 'status', 'created_at',
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    facility = serializers.CharField(source='job.facility_name', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'facility', 'status', 'cover_note', 'applied_at']
        read_only_fields = ['status']

    def create(self, validated_data):
        nurse = self.context['request'].user.nurse_profile
        return JobApplication.objects.create(nurse=nurse, **validated_data)
