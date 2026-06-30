from django.db import models
from accounts.models import User


class NurseProfile(models.Model):
    CATEGORY_CHOICES = [
        ('registered', 'Registered Nurse'),
        ('enrolled', 'Enrolled Nurse'),
        ('auxiliary', 'Auxiliary Nurse'),
        ('specialist', 'Specialist Nurse'),
        ('midwife', 'Midwife'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    PROVINCE_CHOICES = [
        ('GP', 'Gauteng'),
        ('WC', 'Western Cape'),
        ('KZN', 'KwaZulu-Natal'),
        ('EC', 'Eastern Cape'),
        ('FS', 'Free State'),
        ('LP', 'Limpopo'),
        ('MP', 'Mpumalanga'),
        ('NC', 'Northern Cape'),
        ('NW', 'North West'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='nurse_profile')
    id_number = models.CharField(max_length=13, unique=True)
    phone = models.CharField(max_length=15)
    sanc_number = models.CharField(max_length=50, unique=True)
    nursing_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    speciality = models.CharField(max_length=100, blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    province = models.CharField(max_length=3, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.get_full_name()} — {self.sanc_number}'


class NurseDocument(models.Model):
    DOCUMENT_TYPES = [
        ('sanc_certificate', 'SANC Certificate'),
        ('id_document', 'ID Document'),
        ('cv', 'Curriculum Vitae'),
        ('qualification', 'Qualification Certificate'),
        ('reference', 'Reference Letter'),
        ('criminal_clearance', 'Criminal Clearance'),
    ]

    nurse = models.ForeignKey(NurseProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='nurse_documents/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.nurse} — {self.document_type}'


class NurseAvailability(models.Model):
    DAY_CHOICES = [
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday'),
    ]

    SHIFT_CHOICES = [
        ('day', 'Day Shift'),
        ('night', 'Night Shift'),
        ('both', 'Day & Night'),
    ]

    nurse = models.ForeignKey(NurseProfile, on_delete=models.CASCADE, related_name='availability')
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)

    class Meta:
        unique_together = ['nurse', 'day', 'shift']

    def __str__(self):
        return f'{self.nurse} — {self.day} {self.shift}'
