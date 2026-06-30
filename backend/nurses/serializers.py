from rest_framework import serializers
from accounts.models import User
from .models import NurseProfile, NurseDocument, NurseAvailability

ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class NurseDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseDocument
        fields = ['id', 'document_type', 'file', 'uploaded_at', 'verified']
        read_only_fields = ['verified']

    def validate_file(self, file):
        if file.size > MAX_FILE_SIZE_BYTES:
            raise serializers.ValidationError(
                f'File size must not exceed {MAX_FILE_SIZE_MB}MB. '
                f'Your file is {file.size / (1024 * 1024):.1f}MB.'
            )
        ext = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f'Invalid file type ".{ext}". Allowed types: {", ".join(ALLOWED_EXTENSIONS)}.'
            )
        if hasattr(file, 'content_type') and file.content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                'Invalid file format. Allowed formats: PDF, JPG, PNG, DOC, DOCX.'
            )
        return file


class NurseAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseAvailability
        fields = ['id', 'day', 'shift']


class NurseProfileSerializer(serializers.ModelSerializer):
    documents = NurseDocumentSerializer(many=True, read_only=True)
    availability = NurseAvailabilitySerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = NurseProfile
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 'email',
            'id_number', 'phone', 'sanc_number',
            'nursing_category', 'speciality', 'years_experience',
            'province', 'city', 'status', 'documents', 'availability',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status']

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class NurseProfileUpdateSerializer(serializers.ModelSerializer):
    """Handles updates to both NurseProfile and the related User model."""
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = NurseProfile
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'speciality', 'years_experience', 'province', 'city',
        ]

    def validate_phone(self, value):
        digits = value.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 10:
            raise serializers.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return value

    def validate_email(self, value):
        user = self.instance.user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        # Update User model fields
        if user_data:
            for attr, val in user_data.items():
                setattr(instance.user, attr, val)
            instance.user.save()
        # Update NurseProfile fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance


class NurseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NurseProfile
        fields = [
            'id_number', 'phone', 'sanc_number', 'nursing_category',
            'speciality', 'years_experience', 'province', 'city',
        ]

    def validate_phone(self, value):
        digits = value.replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 10:
            raise serializers.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return value

    def validate_id_number(self, value):
        if not value.isdigit() or len(value) != 13:
            raise serializers.ValidationError('ID number must be exactly 13 digits.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return NurseProfile.objects.create(user=user, **validated_data)
