from django.db import models

# ---------------------------
#  EncounterDiagnosis
# ---------------------------

class EncounterDiagnosis(models.Model):
    id = models.AutoField(primary_key=True)

    encounter = models.ForeignKey(
        'Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
        related_name='diagnoses'
    )
    diagnosis = models.ForeignKey(
        'Diagnosis',
        on_delete=models.CASCADE,
        db_column='diagnosis_id',
        related_name='encounter_diagnoses'
    )

    is_primary = models.BooleanField(default=False)
    notes = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'encounter_diagnosis'
        unique_together = ('encounter', 'diagnosis')
        indexes = [
            models.Index(fields=['diagnosis'], name='idx_ed_diag'),
        ]

    def __str__(self):
        patient_name = f"{self.encounter.patient.first_name} {self.encounter.patient.last_name}"
        return f"{patient_name} - {self.diagnosis.code} {self.diagnosis.name}"


# ---------------------------
#  EncounterProcedure
# ---------------------------

class EncounterProcedure(models.Model):
    id = models.AutoField(primary_key=True)

    encounter = models.ForeignKey(
        'Encounter',
        on_delete=models.CASCADE,
        db_column='encounter_id',
        related_name='procedures'
    )
    procedure = models.ForeignKey(
        'pharmacy.Procedure1',
        on_delete=models.RESTRICT,
        db_column='procedure_id',
        related_name='encounter_procedures'
    )

    quantity = models.PositiveSmallIntegerField(default=1)
    notes = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'encounter_procedure'
        unique_together = ('encounter', 'procedure')
        indexes = [
            models.Index(fields=['procedure'], name='idx_ep_procedure'),
        ]

    def __str__(self):
        # FIXED: use encounter.encounter_id
        return f"Encounter {self.encounter.encounter_id} - Procedure {self.procedure.name} x {self.quantity}"


# ---------------------------
#  Encounter
# ---------------------------

class Encounter(models.Model):
    VISIT_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Follow-up', 'Follow-up'),
        ('Emergency', 'Emergency'),
        ('Procedure', 'Procedure'),
        ('Review', 'Review'),
    ]

    encounter_id = models.AutoField(primary_key=True)

    appointment = models.ForeignKey(
        'appointments.Appointments',
        on_delete=models.CASCADE,
        db_column='appointment_id',
        related_name='encounters'
    )
    patient = models.ForeignKey(
        'patients.Patients',
        on_delete=models.RESTRICT,
        db_column='patient_id',
        related_name='encounters'
    )
    doctor = models.ForeignKey(
        'doctors.Doctors',
        on_delete=models.RESTRICT,
        db_column='doctor_id',
        related_name='encounters'
    )

    encounter_date = models.DateField()
    visit_type = models.CharField(
        max_length=20,
        choices=VISIT_TYPE_CHOICES,
        default='Consultation'
    )
    notes = models.CharField(max_length=255, blank=True, null=True)
    diagnosis_summary = models.CharField(max_length=255, blank=True, null=True)
    treatment_plan = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'encounters'
        indexes = [
            models.Index(fields=['patient'], name='idx_encounter_patient'),
            models.Index(fields=['doctor'], name='idx_encounter_doctor'),
            models.Index(fields=['encounter_date'], name='idx_encounter_date'),
        ]

    # ✔ Correct Encounter __str__
    def __str__(self):
        return f"Encounter {self.encounter_id} - {self.patient.first_name} {self.patient.last_name} on {self.encounter_date}"


# ---------------------------
#  Diagnosis
# ---------------------------

class Diagnosis(models.Model):
    diagnosis_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'diagnosis'
        indexes = [
            models.Index(fields=['name'], name='idx_diag_name'),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
