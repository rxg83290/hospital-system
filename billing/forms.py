from django import forms
from .models import Bill, BillLine, Payment

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['encounter', 'patient', 'total_amount', 'status', 'payment_due']
        widgets = {
            #'bill_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_due': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
        }

    bill_date = forms.DateField(
        label='Bill Date',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'})
    )



class BillLineForm(forms.ModelForm):
    class Meta:
        model = BillLine
        fields = ['bill', 'line_type', 'procedure', 'medication', 'description1', 'quantity', 'unit_price']
        widgets = {
            'bill': forms.Select(attrs={'class': 'form-select'}),
            'line_type': forms.Select(attrs={'class': 'form-select'}),
            'procedure': forms.Select(attrs={'class': 'form-select'}),
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'description1': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }





class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['bill', 'amount', 'method', 'status', 'reference']
        widgets = {
            'method': forms.Select(),
            'status': forms.Select(),
        }
