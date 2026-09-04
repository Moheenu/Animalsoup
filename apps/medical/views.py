from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date
from .models import Vaccination
from .forms import VaccinationForm
from apps.pets.models import Pet

@login_required
def vaccination_list(request):
    """View all vaccinations for user's pets"""
    
    # Get all vaccinations for user's pets
    vaccinations = Vaccination.objects.filter(
        pet__owner=request.user,
        is_active=True
    ).select_related('pet')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'completed':
            vaccinations = vaccinations.filter(status=Vaccination.Status.COMPLETED)
        elif status_filter == 'upcoming':
            vaccinations = vaccinations.filter(status=Vaccination.Status.UPCOMING)
        elif status_filter == 'overdue':
            vaccinations = vaccinations.filter(status=Vaccination.Status.OVERDUE)
    
    # Filter by pet
    pet_filter = request.GET.get('pet')
    if pet_filter:
        vaccinations = vaccinations.filter(pet_id=pet_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        vaccinations = vaccinations.filter(
            Q(vaccine_name__icontains=search_query) |
            Q(pet__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(vaccinations, 10)
    page_number = request.GET.get('page')
    vaccinations = paginator.get_page(page_number)
    
    # Get user's pets for filter dropdown
    pets = Pet.objects.filter(owner=request.user, is_active=True)
    
    # Statistics
    stats = {
        'total': Vaccination.objects.filter(pet__owner=request.user, is_active=True).count(),
        'completed': Vaccination.objects.filter(pet__owner=request.user, is_active=True, status=Vaccination.Status.COMPLETED).count(),
        'upcoming': Vaccination.objects.filter(pet__owner=request.user, is_active=True, status=Vaccination.Status.UPCOMING).count(),
        'overdue': Vaccination.objects.filter(pet__owner=request.user, is_active=True, status=Vaccination.Status.OVERDUE).count(),
    }
    
    context = {
        'vaccinations': vaccinations,
        'pets': pets,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
        'pet_filter': pet_filter,
    }
    return render(request, 'medical/vaccination_list.html', context)

@login_required
def vaccination_add(request):
    """Add a new vaccination record"""
    
    if request.method == 'POST':
        form = VaccinationForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            vaccination = form.save()
            messages.success(request, f'Vaccination record for {vaccination.pet.name} added successfully!')
            return redirect('medical:vaccination_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VaccinationForm(request.user)
    
    context = {
        'form': form,
        'title': 'Add Vaccination',
    }
    return render(request, 'medical/vaccination_form.html', context)

@login_required
def vaccination_detail(request, pk):
    """View vaccination details"""
    vaccination = get_object_or_404(Vaccination, pk=pk, pet__owner=request.user)
    
    context = {
        'vaccination': vaccination,
        'title': f'{vaccination.vaccine_name} - {vaccination.pet.name}',
    }
    return render(request, 'medical/vaccination_detail.html', context)

@login_required
def vaccination_edit(request, pk):
    """Edit vaccination record"""
    vaccination = get_object_or_404(Vaccination, pk=pk, pet__owner=request.user)
    
    if request.method == 'POST':
        form = VaccinationForm(request.user, request.POST, request.FILES, instance=vaccination)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vaccination record updated successfully!')
            return redirect('medical:vaccination_detail', pk=vaccination.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VaccinationForm(request.user, instance=vaccination)
    
    context = {
        'form': form,
        'vaccination': vaccination,
        'title': f'Edit {vaccination.vaccine_name}',
    }
    return render(request, 'medical/vaccination_form.html', context)

@login_required
def vaccination_delete(request, pk):
    """Delete (archive) vaccination record"""
    vaccination = get_object_or_404(Vaccination, pk=pk, pet__owner=request.user)
    
    if request.method == 'POST':
        vaccination.is_active = False
        vaccination.save()
        messages.success(request, f'Vaccination record archived successfully!')
        return redirect('medical:vaccination_list')
    
    context = {
        'vaccination': vaccination,
    }
    return render(request, 'medical/vaccination_delete.html', context)