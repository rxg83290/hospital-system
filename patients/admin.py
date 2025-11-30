# patients/admin.py
from django.contrib import admin
from .models import Patients, InsurancePolicy


admin.site.register(InsurancePolicy)
@admin.register(Patients)
class PatientsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user')
    search_fields = ('first_name', 'last_name')