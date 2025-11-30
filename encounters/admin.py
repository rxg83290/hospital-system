from django.contrib import admin
from .models import Encounter, EncounterProcedure, EncounterDiagnosis, Diagnosis


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = (
        'encounter_id',
        'patient',
        'doctor',
        'encounter_date',
        'visit_type',
    )
    search_fields = ('patient__first_name', 'patient__last_name')


@admin.register(EncounterProcedure)
class EncounterProcedureAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'encounter',
        'procedure',
        'quantity',
        'notes',
    )


@admin.register(EncounterDiagnosis)
class EncounterDiagnosisAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'encounter',
        'diagnosis',
    )


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = (
        'diagnosis_id',
        'code',
        'name',
    )
    search_fields = ('code', 'name')

