from rest_framework import serializers
from .models import NurseProfile, NurseDocument, NurseAvailability


class NurseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseDocument
        fields = ['id', 'document_type', 'file', 'uploaded_at', 'verified']
        read_only_fields = ['verified']


class NurseAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseAvailability
        fields = ['id', 'day', 'shift']


class NurseProfileSerializer(serializers.ModelSerializer):
    documents = NurseDocumentSerializer(many=True, read_only=True)
    availability = NurseAvailabilitySerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = NurseProfile
        fields = [
            'id', 'full_name', 'id_number', 'phone', 'sanc_number',
            'nursing_category', 'speciality', 'years_experience',
            'province', 'city', 'status', 'documents', 'availability',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class NurseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseProfile
        fields = [
            'id_number', 'phone', 'sanc_number', 'nursing_category',
            'speciality', 'years_experience', 'province', 'city',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        return NurseProfile.objects.create(user=user, **validated_data)
