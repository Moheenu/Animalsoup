from django import forms
from .models import Vaccination

class VaccinationForm(forms.ModelForm):
    class Meta:
        model = Vaccination
        fields = [
            'pet', 'vaccine_name', 'vaccine_type', 'date_administered',
            'next_due_date', 'expiry_date', 'veterinarian', 'clinic_name',
            'batch_number', 'notes', 'certificate'
        ]
        widgets = {
            'pet': forms.Select(attrs={'class': 'form-control'}),
            'vaccine_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vaccine_type': forms.Select(attrs={'class': 'form-control'}),
            'date_administered': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'veterinarian': forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'pet': 'Pet',
            'vaccine_name': 'Vaccine Name',
            'vaccine_type': 'Vaccine Type',
            'date_administered': 'Date Administered',
            'next_due_date': 'Next Due Date',
            'expiry_date': 'Expiry Date',
            'veterinarian': 'Veterinarian',
            'clinic_name': 'Clinic Name',
            'batch_number': 'Batch/Lot Number',
            'notes': 'Notes',
            'certificate': 'Certificate/Document',
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show pets belonging to the current user
        if user:
            self.fields['pet'].queryset = user.pets.filter(is_active=True)