from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import Appointments
from patients.models import Patients


# Fixed 30-minute time slots (8–10, 12–3)
TIME_SLOT_CHOICES = [
    ("08:00", "08:00 – 08:30"),
    ("08:30", "08:30 – 09:00"),
    ("09:00", "09:00 – 09:30"),
    ("09:30", "09:30 – 10:00"),

    ("12:00", "12:00 – 12:30"),
    ("12:30", "12:30 – 13:00"),
    ("13:00", "13:00 – 13:30"),
    ("13:30", "13:30 – 14:00"),

    ("14:00", "14:00 – 14:30"),
    ("14:30", "14:30 – 15:00"),
]


class AppointmentForm(forms.ModelForm):
    """
    Form used in the patient portal.
    - No patient field: patient is passed in from the view.
    - Start time is chosen from fixed slots.
    - End time is auto-calculated.
    - Status is forced to BOOKED.
    """

    # dropdown of fixed time slots
    start_time = forms.TypedChoiceField(
        label="Start time",
        choices=TIME_SLOT_CHOICES,
        coerce=lambda v: datetime.strptime(v, "%H:%M").time(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        # patient is provided by the view (AppointmentCreateView)
        self.patient = kwargs.pop("patient", None)
        super().__init__(*args, **kwargs)

        if self.patient is None:
            raise ValueError("AppointmentForm requires a 'patient' keyword argument.")

    class Meta:
        model = Appointments
        # NOTE: no patient and no status here; no end_time input
        fields = [
            "doctor",
            "appointment_date",
            "start_time",
            "reason",
        ]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-select"}),
            "appointment_date": forms.DateInput(attrs={
                "class": "form-control",
                "placeholder": "YYYY-MM-DD",
                "id": "appointment_date",
                "type": "date",
            }),
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get("appointment_date")
        today = datetime.now().date()

        if appointment_date and appointment_date < today:
            raise ValidationError("You cannot book an appointment in the past.")

        return appointment_date

    def clean(self):
        cleaned_data = super().clean()

        doctor = cleaned_data.get("doctor")
        appointment_date = cleaned_data.get("appointment_date")
        start_time = cleaned_data.get("start_time")

        # Get current date & time
        today = datetime.now().date()
        now_time = datetime.now().time()

        # ---- 1. Prevent past date ----
        if appointment_date:
            if appointment_date < today:
                raise ValidationError("You cannot book an appointment in the past.")

            # ---- 2. Prevent past time slots today ----
            if appointment_date == today and start_time and start_time < now_time:
                raise ValidationError("You cannot book a time slot that has already passed today.")

        # ---- 3. Continue with your normal overlap validation ----
        if doctor and appointment_date and start_time:
            dt_start = datetime.combine(appointment_date, start_time)
            end_time = (dt_start + timedelta(minutes=30)).time()
            cleaned_data["computed_end_time"] = end_time

            # check overlap with other appointments
            qs = Appointments.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            overlap = qs.filter(
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()

            if overlap:
                raise ValidationError(
                    "This doctor already has an appointment in that time slot. "
                    "Please choose another time."
                )

        return cleaned_data


    def save(self, commit=True):
        appointment = super().save(commit=False)

        # link to logged-in patient from the view
        appointment.patient = self.patient

        # set end_time from the computed value
        appointment.end_time = self.cleaned_data.get("computed_end_time")

        # force BOOKED status
        appointment.status = "BOOKED"

        if commit:
            appointment.save()
        return appointment


