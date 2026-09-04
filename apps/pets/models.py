from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image

User = get_user_model()

class Pet(models.Model):
    """Pet model with complete profile information"""
    
    class Species(models.TextChoices):
        DOG = 'DOG', 'Dog'
        CAT = 'CAT', 'Cat'
        BIRD = 'BIRD', 'Bird'
        FISH = 'FISH', 'Fish'
        RABBIT = 'RABBIT', 'Rabbit'
        HAMSTER = 'HAMSTER', 'Hamster'
        REPTILE = 'REPTILE', 'Reptile'
        HORSE = 'HORSE', 'Horse'
        OTHER = 'OTHER', 'Other'
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        UNKNOWN = 'U', 'Unknown'
    
    class BloodGroup(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'
        AB = 'AB', 'AB'
        O = 'O', 'O'
        UNKNOWN = 'UNKNOWN', 'Unknown'
    
    # Basic Information
    pet_id = models.CharField(max_length=20, unique=True, blank=True, 
                              help_text="Unique pet identification number")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=Species.choices, default=Species.DOG)
    breed = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.UNKNOWN)
    
    # Physical Attributes
    date_of_birth = models.DateField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                 help_text="Weight in kg")
    microchip_number = models.CharField(max_length=50, blank=True, null=True)
    blood_group = models.CharField(max_length=10, choices=BloodGroup.choices, 
                                   default=BloodGroup.UNKNOWN)
    
    # Medical Information
    allergies = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)
    emergency_notes = models.TextField(blank=True, null=True)
    
    # Media
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pets'
        ordering = ['-created_at']
        verbose_name = 'Pet'
        verbose_name_plural = 'Pets'
    
    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"
    
    def save(self, *args, **kwargs):
        # Generate Pet ID if not provided
        if not self.pet_id:
            self.pet_id = f"PET-{uuid.uuid4().hex[:8].upper()}"
        
        # Generate QR code if not exists
        if not self.qr_code:
            self.generate_qr_code()
        
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        """Generate QR code with emergency information"""
        try:
            # Create QR code data
            qr_data = {
                'pet_id': self.pet_id,
                'name': self.name,
                'species': self.get_species_display(),
                'breed': self.breed or 'Unknown',
                'allergies': self.allergies or 'None',
                'medical_conditions': self.medical_conditions or 'None',
                'emergency': self.emergency_notes or 'No emergency information',
            }
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(str(qr_data))
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to BytesIO
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            # Create Django File
            filename = f"qr_{self.pet_id}.png"
            self.qr_code.save(filename, File(buffer), save=False)
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
    
    @property
    def age(self):
        """Calculate age automatically"""
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or \
               (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return None
    
    @property
    def age_display(self):
        """Display age in years and months"""
        if not self.date_of_birth:
            return "Unknown"
        age = self.age
        if age is None:
            return "Unknown"
        if age == 0:
            return "< 1 year"
        elif age == 1:
            return "1 year"
        else:
            return f"{age} years"
    
    def get_emergency_info(self):
        """Get emergency information for QR code"""
        return {
            'pet_name': self.name,
            'species': self.get_species_display(),
            'breed': self.breed or 'Unknown',
            'allergies': self.allergies or 'None',
            'medical_conditions': self.medical_conditions or 'None',
            'emergency_notes': self.emergency_notes or 'None',
            'owner': self.owner.full_name,
            'owner_phone': self.owner.phone or 'Not provided',
            'pet_id': self.pet_id,
        }


class PetHealthRecord(models.Model):
    """Health records for pets"""
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='health_records')
    
    condition = models.CharField(max_length=200)
    diagnosis = models.TextField(blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    doctor_contact = models.CharField(max_length=20, blank=True, null=True)
    
    date_visited = models.DateField(default=timezone.now)
    follow_up_date = models.DateField(blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    prescription = models.TextField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pet_health_records'
        ordering = ['-date_visited']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'
    
    def __str__(self):
        return f"{self.pet.name} - {self.condition} ({self.date_visited})"