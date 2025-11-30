from django.db import models

# Create your models here.

class Bill(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    bill_id = models.AutoField(primary_key=True)
    encounter = models.ForeignKey(
        'encounters.Encounter',  
        on_delete=models.CASCADE,
        db_column='encounter_id',
        related_name='bills'
    )
    patient = models.ForeignKey(
        'patients.Patients',  
        on_delete=models.RESTRICT,
        db_column='patient_id',
        related_name='bills'
    )
    bill_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    payment_due = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'bill'
        indexes = [
            models.Index(fields=['patient'], name='idx_bill_patient'),
            models.Index(fields=['encounter'], name='idx_bill_encounter'),
        ]

    def __str__(self):
        return f"Bill {self.bill_id} - {self.patient.first_name} {self.patient.last_name} - {self.status}"



class BillLine(models.Model):
    LINE_TYPE_CHOICES = [
        ('PROCEDURE', 'Procedure'),
        ('MEDICATION', 'Medication'),
        ('SERVICE', 'Service'),
    ]

    bill_line_id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(
        'Bill',  
        on_delete=models.CASCADE,
        db_column='bill_id',
        related_name='bill_lines'
    )
    line_type = models.CharField(max_length=10, choices=LINE_TYPE_CHOICES)
    procedure = models.ForeignKey(
        'pharmacy.Procedure1',  
        on_delete=models.RESTRICT,
        db_column='procedure_id',
        blank=True,
        null=True,
        related_name='bill_lines'
    )
    medication = models.ForeignKey(
        'pharmacy.Medication',  
        on_delete=models.RESTRICT,
        db_column='medication_id',
        blank=True,
        null=True,
        related_name='bill_lines'
    )
    description1 = models.CharField(max_length=120, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = 'bill_line'
        indexes = [
            models.Index(fields=['bill'], name='idx_bill_line_bill'),
            models.Index(fields=['procedure'], name='idx_bill_line_proc'),
            models.Index(fields=['medication'], name='idx_bill_line_med'),
        ]

    @property
    def calculated_total(self):
        return (self.quantity or 0) * (self.unit_price or 0)

    def __str__(self):
        if self.line_type == 'MEDICATION' and self.medication:
            item = self.medication.generic_name
        elif self.line_type == 'PROCEDURE' and self.procedure:
            item = self.procedure.name
        else:
            item = self.description1 or "Service"
        return f"BillLine {self.bill_line_id} - {item} x {self.quantity}"




class Payment(models.Model):
    METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('MPESA', 'Mpesa'),
        ('INSURANCE', 'Insurance'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    ]

    payment_id = models.AutoField(primary_key=True)
    bill = models.ForeignKey(
        'Bill', 
        on_delete=models.CASCADE,
        db_column='bill_id',
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SUCCESS'
    )
    reference = models.CharField(max_length=40, blank=True, null=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'
        indexes = [
            models.Index(fields=['bill'], name='idx_payment_bill'),
            models.Index(fields=['method'], name='idx_payment_method'),
        ]

    def __str__(self):
        return f"Payment {self.payment_id} - Bill {self.bill.bill_id} - {self.amount} via {self.method} ({self.status})"

