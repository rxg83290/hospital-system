from django.db import models

# Create your models here.

class Procedure1(models.Model):
    procedure_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)  
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True, null=True)
    department = models.ForeignKey(
        'doctors.Department',        
        on_delete=models.SET_NULL,
        db_column='department_id',
        related_name='procedures',
        blank=True,
        null=True
    )
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'procedure1'
        indexes = [
            models.Index(fields=['name'], name='idx_proc_name'),
            models.Index(fields=['department'], name='idx_proc_dept'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Medication(models.Model):
    FORM_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Capsule', 'Capsule'),
        ('Syrup', 'Syrup'),
        ('Injection', 'Injection'),
        ('Inhaler', 'Inhaler'),
        ('Drops', 'Drops'),
        ('Cream', 'Cream'),
        ('Other', 'Other'),
    ]

    medication_id = models.AutoField(primary_key=True)
    generic_name = models.CharField(max_length=50)
    brand_name = models.CharField(max_length=50, blank=True, null=True)
    form = models.CharField(
        max_length=10,
        choices=FORM_CHOICES,
        default='Tablet'
    )
    strength = models.CharField(max_length=30, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False
        db_table = 'medication'

    def __str__(self):
        return f"{self.generic_name} ({self.brand_name}) - {self.form}"


class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(
        'encounters.Encounter',  
        on_delete=models.CASCADE,
        db_column='encounter_id',
        related_name='prescriptions'
    )
    medication = models.ForeignKey(
        'Medication',  
        on_delete=models.RESTRICT,
        db_column='medication_id',
        related_name='prescriptions'
    )
    dosage = models.CharField(max_length=30)
    frequency_per_day = models.PositiveIntegerField(default=1)
    duration_days = models.PositiveSmallIntegerField(default=7)
    instructions = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        managed = False
        db_table = 'prescription'
        indexes = [
            models.Index(fields=['encounter'], name='idx_prescription_encounter'),
            models.Index(fields=['medication'], name='idx_prescription_medication'),
        ]

    def __str__(self):
        return f"Prescription {self.prescription_id} - {self.medication.generic_name} for Encounter {self.encounter.encounter_id}"
