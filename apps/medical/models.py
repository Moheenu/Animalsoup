from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from apps.pets.models import Pet

User = get_user_model()

class Vaccination(models.Model):
    """Vaccination records for pets"""
    
    class VaccineType(models.TextChoices):
        CORE = 'CORE', 'Core Vaccine'
        NON_CORE = 'NON_CORE', 'Non-Core Vaccine'
        RABIES = 'RABIES', 'Rabies'
        DHPP = 'DHPP', 'DHPP (Distemper/Parvo)'
        BORDETELLA = 'BORDETELLA', 'Bordetella'
        LEPTOSPIROSIS = 'LEPTOSPIROSIS', 'Leptospirosis'
        LYME = 'LYME', 'Lyme Disease'
        FELV = 'FELV', 'Feline Leukemia'
        FVRCP = 'FVRCP', 'FVRCP (Feline Distemper)'
        OTHER = 'OTHER', 'Other'
    
    class Status(models.TextChoices):
        COMPLETED = 'COMPLETED', 'Completed'
        UPCOMING = 'UPCOMING', 'Upcoming'
        OVERDUE = 'OVERDUE', 'Overdue'
    
    # Basic Information
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=200)
    vaccine_type = models.CharField(max_length=20, choices=VaccineType.choices, default=VaccineType.CORE)
    
    # Dates
    date_administered = models.DateField(default=timezone.now)
    next_due_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # Additional Information
    veterinarian = models.CharField(max_length=100, blank=True, null=True)
    clinic_name = models.CharField(max_length=200, blank=True, null=True)
    batch_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Documents
    certificate = models.FileField(upload_to='vaccination_certificates/', blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vaccinations'
        ordering = ['-date_administered']
        verbose_name = 'Vaccination'
        verbose_name_plural = 'Vaccinations'
    
    def __str__(self):
        return f"{self.pet.name} - {self.vaccine_name} ({self.date_administered})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate next due date if not provided
        if not self.next_due_date and self.date_administered:
            # Default to 1 year for most vaccines
            self.next_due_date = self.date_administered + timedelta(days=365)
        
        # Update status based on dates
        self.update_status()
        
        super().save(*args, **kwargs)
    
    def update_status(self):
        """Update vaccination status based on dates"""
        today = date.today()
        
        if not self.next_due_date:
            self.status = self.Status.COMPLETED
            return
        
        if self.next_due_date < today:
            self.status = self.Status.OVERDUE
        elif (self.next_due_date - today).days <= 30:
            self.status = self.Status.UPCOMING
        else:
            self.status = self.Status.COMPLETED
    
    @property
    def days_until_due(self):
        """Get days until next due date"""
        if not self.next_due_date:
            return None
        delta = self.next_due_date - date.today()
        return delta.days
    
    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
    
    @property
    def is_upcoming(self):
        return self.status == self.Status.UPCOMING
    
    @property
    def is_overdue(self):
        return self.status == self.Status.OVERDUE
    
    @property
    def status_icon(self):
        """Get emoji status indicator"""
        if self.is_completed:
            return '🟢'
        elif self.is_upcoming:
            return '🟡'
        elif self.is_overdue:
            return '🔴'
        return '⚪'
    
    @property
    def status_color(self):
        """Get Bootstrap color class"""
        if self.is_completed:
            return 'success'
        elif self.is_upcoming:
            return 'warning'
        elif self.is_overdue:
            return 'danger'
        return 'secondary'
    
    @property
    def vaccination_age(self):
        """Calculate how long ago the vaccination was administered"""
        if not self.date_administered:
            return None
        delta = date.today() - self.date_administered
        return delta.days


class VaccinationReminder(models.Model):
    """Reminders for upcoming vaccinations"""
    
    vaccination = models.OneToOneField(Vaccination, on_delete=models.CASCADE, related_name='reminder')
    reminder_date = models.DateField()
    reminder_sent = models.BooleanField(default=False)
    reminder_type = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('NOTIFICATION', 'Notification'),
    ], default='NOTIFICATION')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'vaccination_reminders'
    
    def __str__(self):
        return f"Reminder for {self.vaccination.pet.name} - {self.vaccination.vaccine_name}"