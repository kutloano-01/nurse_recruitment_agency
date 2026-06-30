from django.db import models
from accounts.models import User


class EmployerProfile(models.Model):
    FACILITY_TYPES = [
        ('public_hospital', 'Public Hospital'),
        ('private_hospital', 'Private Hospital'),
        ('clinic', 'Clinic'),
        ('home_care', 'Home Care Provider'),
        ('frail_care', 'Frail Care Facility'),
        ('other', 'Other'),
    ]

    PROVINCE_CHOICES = [
        ('GP', 'Gauteng'), ('WC', 'Western Cape'), ('KZN', 'KwaZulu-Natal'),
        ('EC', 'Eastern Cape'), ('FS', 'Free State'), ('LP', 'Limpopo'),
        ('MP', 'Mpumalanga'), ('NC', 'Northern Cape'), ('NW', 'North West'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    facility_name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=30, choices=FACILITY_TYPES)
    province = models.CharField(max_length=3, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=100)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.facility_name


class StaffingRequest(models.Model):
    URGENCY_CHOICES = [
        ('immediate', 'Immediate (within 24hrs)'),
        ('urgent', 'Urgent (within 48hrs)'),
        ('planned', 'Planned (more than 48hrs)'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
    ]

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='staffing_requests')
    nursing_category = models.CharField(max_length=20)
    speciality = models.CharField(max_length=100, blank=True)
    number_of_nurses = models.PositiveIntegerField(default=1)
    shift_type = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='planned')
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.employer} — {self.nursing_category} x{self.number_of_nurses}'
