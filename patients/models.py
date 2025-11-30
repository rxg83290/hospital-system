from django.db import models
from django.db import models
from django.conf import settings
# Create your models here.

class Patients(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    patient_id = models.AutoField(primary_key=True)  
    mrn = models.CharField(max_length=10, unique=True)  
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()  
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)  
    phone = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  
    updated_at = models.DateTimeField(auto_now=True, null=True)      

    class Meta:
        managed = True  
        db_table = 'patients'
        indexes = [
            models.Index(fields=['last_name', 'first_name'], name='idx_patient_name'),  
        ]

    def __str__(self):
        return f"{self.mrn} - {self.first_name} {self.last_name}"


class InsurancePolicy(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EXPIRED', 'Expired'),
    ]

    policy_id = models.AutoField(primary_key=True)  
    patient = models.ForeignKey(
        'Patients',
        on_delete=models.CASCADE,
        db_column='patient_id',
        related_name='policies'
    )

    payer_name = models.CharField(max_length=60)
    plan_name = models.CharField(max_length=60, blank=True, null=True)
    policy_number = models.CharField(max_length=40, unique=True)
    group_number = models.CharField(max_length=40, blank=True, null=True)

    coverage_start = models.DateField()
    coverage_end = models.DateField(blank=True, null=True)
    coverage_percent = models.PositiveSmallIntegerField(default=80)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    copay_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    is_primary = models.BooleanField(default=True)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'insurance_policy'
        indexes = [
            models.Index(fields=['patient'], name='idx_policy_patient'),
            models.Index(fields=['payer_name'], name='idx_policy_payer'),
            models.Index(fields=['status'], name='idx_policy_status'),
        ]

    def __str__(self):
        return f"{self.policy_number} ({self.payer_name})"
