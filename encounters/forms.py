from django import forms
from .models import EncounterDiagnosis, EncounterProcedure, Encounter, Diagnosis

class EncounterDiagnosisForm(forms.ModelForm):
    class Meta:
        model = EncounterDiagnosis
        fields = ['encounter', 'diagnosis', 'is_primary', 'notes']
        widgets = {
            'encounter': forms.Select(attrs={'class': 'form-select'}),
            'diagnosis': forms.Select(attrs={'class': 'form-select'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class EncounterProcedureForm(forms.ModelForm):
    class Meta:
        model = EncounterProcedure
        fields = ['encounter', 'procedure', 'quantity', 'notes']
        widgets = {
            'encounter': forms.Select(attrs={'class': 'form-select'}),
            'procedure': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class EncounterForm(forms.ModelForm):
    class Meta:
        model = Encounter
        fields = [
            'appointment', 'patient', 'doctor', 'encounter_date', 
            'visit_type', 'notes', 'diagnosis_summary', 'treatment_plan'
        ]
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'encounter_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visit_type': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnosis_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model = Diagnosis
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
