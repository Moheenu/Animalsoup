from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from apps.pets.models import Pet

User = get_user_model()


class Reminder(models.Model):
    """Reminder system for pet care tasks"""
    
    class ReminderType(models.TextChoices):
        VACCINATION = 'VACCINATION', 'Vaccination'
        DEWORMING = 'DEWORMING', 'Deworming'
        MEDICATION = 'MEDICATION', 'Medication'
        VET_APPOINTMENT = 'VET_APPOINTMENT', 'Vet Appointment'
        GROOMING = 'GROOMING', 'Grooming'
        DENTAL = 'DENTAL', 'Dental Checkup'
        LICENSE = 'LICENSE', 'Pet License Renewal'
        FLEA_TICK = 'FLEA_TICK', 'Flea/Tick Treatment'
        FEEDING = 'FEEDING', 'Feeding'
        HEALTH_CHECKUP = 'HEALTH_CHECKUP', 'Health Checkup'
        CUSTOM = 'CUSTOM', 'Custom'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        OVERDUE = 'OVERDUE', 'Overdue'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'
    
    # Basic Information
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reminders'
    )
    pet = models.ForeignKey(
        Pet, 
        on_delete=models.CASCADE, 
        related_name='reminders', 
        null=True, 
        blank=True
    )
    
    title = models.CharField(max_length=200)
    reminder_type = models.CharField(
        max_length=20, 
        choices=ReminderType.choices, 
        default=ReminderType.CUSTOM
    )
    description = models.TextField(blank=True, null=True)
    
    # Dates and Times
    reminder_date = models.DateField()
    reminder_time = models.TimeField(blank=True, null=True)
    repeat_interval = models.IntegerField(
        default=0, 
        help_text="Repeat every X days (0 = no repeat)"
    )
    
    # Status
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    priority = models.CharField(
        max_length=10, 
        choices=Priority.choices, 
        default=Priority.MEDIUM
    )
    
    # Notifications
    notify_by_email = models.BooleanField(default=False)
    notify_by_sms = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    
    # Additional Info
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminders'
        ordering = ['reminder_date', 'reminder_time']
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
    
    def __str__(self):
        pet_name = self.pet.name if self.pet else 'General'
        return f"{self.title} - {pet_name} ({self.reminder_date})"
    
    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)
    
    def update_status(self):
        """Update reminder status based on date"""
        today = date.today()
        
        # Don't change status if already completed or cancelled
        if self.status in [self.Status.COMPLETED, self.Status.CANCELLED]:
            return
        
        # Update based on date
        if self.reminder_date < today:
            self.status = self.Status.OVERDUE
        elif self.reminder_date == today:
            self.status = self.Status.PENDING
        else:
            self.status = self.Status.PENDING
    
    @property
    def is_pending(self):
        return self.status == self.Status.PENDING
    
    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
    
    @property
    def is_overdue(self):
        return self.status == self.Status.OVERDUE
    
    @property
    def days_until(self):
        """Get days until reminder date"""
        if not self.reminder_date:
            return None
        delta = self.reminder_date - date.today()
        return delta.days
    
    @property
    def status_icon(self):
        """Get emoji for status"""
        if self.is_completed:
            return '✅'
        elif self.is_overdue:
            return '⚠️'
        elif self.days_until == 0:
            return '🔔'
        elif self.days_until and self.days_until <= 3:
            return '⏰'
        return '📌'
    
    @property
    def status_color(self):
        """Get Bootstrap color class for status"""
        if self.is_completed:
            return 'success'
        elif self.is_overdue:
            return 'danger'
        elif self.days_until == 0:
            return 'warning'
        elif self.days_until and self.days_until <= 3:
            return 'warning'
        return 'info'
    
    @property
    def priority_color(self):
        """Get Bootstrap color class for priority"""
        if self.priority == self.Priority.URGENT:
            return 'danger'
        elif self.priority == self.Priority.HIGH:
            return 'warning'
        elif self.priority == self.Priority.MEDIUM:
            return 'info'
        return 'secondary'
    
    @property
    def reminder_type_icon(self):
        """Get emoji for reminder type"""
        icons = {
            'VACCINATION': '💉',
            'DEWORMING': '🐛',
            'MEDICATION': '💊',
            'VET_APPOINTMENT': '🏥',
            'GROOMING': '✂️',
            'DENTAL': '🦷',
            'LICENSE': '📋',
            'FLEA_TICK': '🪳',
            'FEEDING': '🍖',
            'HEALTH_CHECKUP': '🩺',
            'CUSTOM': '📌',
        }
        return icons.get(self.reminder_type, '📌')


class ReminderLog(models.Model):
    """Log of reminder actions"""
    
    class Action(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        UPDATED = 'UPDATED', 'Updated'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NOTIFICATION_SENT = 'NOTIFICATION_SENT', 'Notification Sent'
        REPEATED = 'REPEATED', 'Repeated'
    
    reminder = models.ForeignKey(
        Reminder, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    action = models.CharField(
        max_length=20, 
        choices=Action.choices
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reminder_logs'
        ordering = ['-created_at']
        verbose_name = 'Reminder Log'
        verbose_name_plural = 'Reminder Logs'
    
    def __str__(self):
        return f"{self.reminder.title} - {self.get_action_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"