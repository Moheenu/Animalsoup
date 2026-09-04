from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from apps.pets.models import Pet
from apps.pets.models import PetHealthRecord
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@login_required
def home(request):
    """Main dashboard view"""
    
    # Get user's pets
    pets = Pet.objects.filter(owner=request.user, is_active=True)
    total_pets = pets.count()
    
    # Get recent health records
    recent_records = PetHealthRecord.objects.filter(
        pet__owner=request.user
    ).order_by('-date_visited')[:5]
    
    # Get upcoming reminders (placeholder - we'll implement this later)
    upcoming_reminders = []
    
    # Get upcoming appointments (placeholder - we'll implement this later)
    upcoming_appointments = []
    
    # Quick stats
    stats = {
        'total_pets': total_pets,
        'upcoming_vaccinations': 0,  # Placeholder
        'pending_appointments': 0,   # Placeholder
        'active_reminders': 0,       # Placeholder
    }
    
    context = {
        'pets': pets,
        'total_pets': total_pets,
        'recent_records': recent_records,
        'upcoming_reminders': upcoming_reminders,
        'upcoming_appointments': upcoming_appointments,
        'stats': stats,
    }
    
    return render(request, 'dashboard/home.html', context)