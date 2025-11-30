
from django import forms
from .models import Patients, InsurancePolicy

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patients
        fields = [
            'mrn', 'first_name', 'last_name', 'dob', 'sex',
            'phone', 'email', 'address'
        ]
        widgets = {
            'mrn': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class InsurancePolicyForm(forms.ModelForm):
    class Meta:
        model = InsurancePolicy
        fields = [
            'patient', 'payer_name', 'plan_name', 'policy_number', 'group_number',
            'coverage_start', 'coverage_end', 'coverage_percent',
            'deductible_amount', 'copay_amount', 'is_primary', 'status'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control select2-patient'}),
            'payer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'plan_name': forms.TextInput(attrs={'class': 'form-control'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'group_number': forms.TextInput(attrs={'class': 'form-control'}),
            'coverage_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'coverage_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'coverage_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductible_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'copay_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
