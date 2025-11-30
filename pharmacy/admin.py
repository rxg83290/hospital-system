# patients/admin.py
from django.contrib import admin
from .models import Procedure1, Medication, Prescription

admin.site.register(Procedure1)
admin.site.register(Medication)
admin.site.register(Prescription)