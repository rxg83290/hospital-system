from django.db import models

# Create your models here.


class Appointments(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    appointment_id = models.AutoField(primary_key=True)

    patient = models.ForeignKey(
        'patients.Patients',
        on_delete=models.CASCADE,
        db_column='patient_id',
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        'doctors.Doctors',
        on_delete=models.CASCADE,
        db_column='doctor_id',
        related_name='appointments'
    )

    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='BOOKED'
    )

    # IMPORTANT: since database already contains values, no auto_now_add / auto_now
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'appointments'
        indexes = [
            models.Index(fields=['doctor', 'appointment_date', 'start_time'], name='idx_appt_doctor_time'),
            models.Index(fields=['patient', 'appointment_date', 'start_time'], name='idx_appt_patient_time'),
        ]

    def __str__(self):
        return (
            f"Appointment {self.appointment_id} - "
            f"{self.patient.first_name} {self.patient.last_name} "
            f"with Dr. {self.doctor.last_name} on {self.appointment_date} "
            f"at {self.start_time}"
        )
