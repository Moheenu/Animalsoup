from django import forms
from .models import Reminder
from apps.pets.models import Pet
from django.contrib.auth import get_user_model

User = get_user_model()

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = [
            'pet', 'title', 'reminder_type', 'description',
            'reminder_date', 'reminder_time', 'repeat_interval',
            'priority', 'notify_by_email', 'notify_by_sms', 'notes'
        ]
        widgets = {
            'pet': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reminder_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reminder_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'repeat_interval': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notify_by_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_by_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'pet': 'Pet (Optional)',
            'title': 'Reminder Title',
            'reminder_type': 'Reminder Type',
            'description': 'Description',
            'reminder_date': 'Reminder Date',
            'reminder_time': 'Reminder Time (Optional)',
            'repeat_interval': 'Repeat Every (Days, 0 = No Repeat)',
            'priority': 'Priority',
            'notify_by_email': 'Notify by Email',
            'notify_by_sms': 'Notify by SMS',
            'notes': 'Notes',
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show user's pets
        if user:
            self.fields['pet'].queryset = Pet.objects.filter(owner=user, is_active=True)
            self.fields['pet'].empty_label = "General (No specific pet)"
        
        # Set default date to today
        if not self.instance.pk:
            self.fields['reminder_date'].initial = forms.DateInput().value_from_datadict(
                self.data, self.files, 'reminder_date'
            ) or date.today().isoformat()