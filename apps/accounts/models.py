from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    """Custom user manager with role-based queries"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(username, email, password, **extra_fields)
    
    def owners(self):
        return self.filter(role=User.Role.OWNER)
    
    def veterinarians(self):
        return self.filter(role=User.Role.VETERINARIAN)
    
    def admins(self):
        return self.filter(role=User.Role.ADMIN)


class User(AbstractUser):
    """Custom User model with role-based permissions"""
    
    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Pet Owner'
        VETERINARIAN = 'VET', 'Veterinarian'
        ADMIN = 'ADMIN', 'Administrator'
    
    # Add related_name to avoid conflicts with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Changed from 'user_set'
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Changed from 'user_set'
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.OWNER,
        help_text="User role in the system"
    )
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use the custom manager
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER
    
    @property
    def is_veterinarian(self):
        return self.role == self.Role.VETERINARIAN
    
    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(models.Model):
    """Extended user profile information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ], blank=True, null=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Additional fields
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.username}"