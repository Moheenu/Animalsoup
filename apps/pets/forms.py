from django import forms
from .models import Pet, PetHealthRecord

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = [
            'name', 'species', 'breed', 'gender', 'date_of_birth',
            'color', 'weight', 'microchip_number', 'blood_group',
            'allergies', 'medical_conditions', 'emergency_notes', 'photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PetHealthRecordForm(forms.ModelForm):
    class Meta:
        model = PetHealthRecord
        fields = [
            'condition', 'diagnosis', 'symptoms', 'treatment',
            'doctor_name', 'doctor_contact', 'date_visited',
            'follow_up_date', 'notes', 'prescription'
        ]
        widgets = {
            'date_visited': forms.DateInput(attrs={'type': 'date'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'