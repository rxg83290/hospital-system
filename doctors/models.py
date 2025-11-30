from django.db import models
from django.db import models
from django.conf import settings
# Create your models here.

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=30, unique=True)  
    location = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  
    updated_at = models.DateTimeField(auto_now=True, null=True)      

    class Meta:
        managed = False  
        db_table = 'department'

    def __str__(self):
        return self.name




class Doctors(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    doctor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    specialization = models.CharField(max_length=50)
    phone = models.CharField(max_length=10, blank=True, null=True)
    email = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(
        'Department',
        on_delete=models.RESTRICT,
        db_column='department_id',
        related_name='doctors',
        null = True,
        blank = True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = True
        db_table = 'doctors'
        indexes = [
            models.Index(fields=['last_name', 'first_name'], name='idx_doctor_name'),
            models.Index(fields=['department'], name='idx_doctor_department'),
        ]

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"
