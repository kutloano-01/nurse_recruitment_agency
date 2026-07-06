from django.db import models
from nurses.models import NurseProfile


class Job(models.Model):
    CONTRACT_TYPES = [
        ('full_time', 'Full Time'),
        ('contract', 'Contract'),
        ('locum', 'Locum / Agency'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('filled', 'Filled'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    PROVINCE_CHOICES = [
        ('GP', 'Gauteng'), ('WC', 'Western Cape'), ('KZN', 'KwaZulu-Natal'),
        ('EC', 'Eastern Cape'), ('FS', 'Free State'), ('LP', 'Limpopo'),
        ('MP', 'Mpumalanga'), ('NC', 'Northern Cape'), ('NW', 'North West'),
    ]

    title = models.CharField(max_length=200)
    facility_name = models.CharField(max_length=200)
    province = models.CharField(max_length=3, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    nursing_category = models.CharField(max_length=50)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_display = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.facility_name}'


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('placed', 'Placed'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    nurse = models.ForeignKey(NurseProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_note = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['job', 'nurse']

    def __str__(self):
        return f'{self.nurse} → {self.job}'
