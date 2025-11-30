from django import forms
from .models import Procedure1, Medication, Prescription

class Procedure1Form(forms.ModelForm):
    class Meta:
        model = Procedure1
        fields = ['code', 'name', 'description', 'department', 'duration_minutes', 'base_price']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Procedure code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Procedure name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['generic_name', 'brand_name', 'form', 'strength', 'unit_price']
        widgets = {
            'generic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand_name': forms.TextInput(attrs={'class': 'form-control'}),
            'form': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tablet, Syrup, etc.'}),
            'strength': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '500mg'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['encounter', 'medication', 'dosage', 'frequency_per_day', 'duration_days', 'instructions']
        widgets = {
            'encounter': forms.Select(attrs={'class': 'form-select'}),
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 tablet'}),
            'frequency_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'duration_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Take with food, etc.'}),
        }
