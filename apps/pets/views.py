from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import Pet, PetHealthRecord
from .forms import PetForm, PetHealthRecordForm

User = get_user_model()

@login_required
def pet_list(request):
    """View all pets of the current user"""
    pets = Pet.objects.filter(owner=request.user, is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        pets = pets.filter(name__icontains=search_query) | \
               pets.filter(breed__icontains=search_query)
    
    # Pagination
    paginator = Paginator(pets, 10)
    page_number = request.GET.get('page')
    pets = paginator.get_page(page_number)
    
    context = {
        'pets': pets,
        'search_query': search_query,
        'total_pets': pets.paginator.count if hasattr(pets, 'paginator') else len(pets),
    }
    return render(request, 'pets/list.html', context)

@login_required
def pet_add(request):
    """Add a new pet"""
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = request.user
            pet.save()
            messages.success(request, f'{pet.name} has been added successfully!')
            return redirect('pets:detail', pk=pet.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PetForm()
    
    context = {
        'form': form,
        'title': 'Add New Pet',
    }
    return render(request, 'pets/add.html', context)

@login_required
def pet_detail(request, pk):
    """View pet details"""
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    health_records = pet.health_records.all()[:5]  # Last 5 records
    
    context = {
        'pet': pet,
        'health_records': health_records,
        'emergency_info': pet.get_emergency_info(),
    }
    return render(request, 'pets/detail.html', context)

@login_required
def pet_edit(request, pk):
    """Edit pet details"""
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, f'{pet.name} has been updated successfully!')
            return redirect('pets:detail', pk=pet.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PetForm(instance=pet)
    
    context = {
        'form': form,
        'pet': pet,
        'title': f'Edit {pet.name}',
    }
    return render(request, 'pets/add.html', context)

@login_required
def pet_delete(request, pk):
    """Delete (archive) a pet"""
    pet = get_object_or_404(Pet, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        pet.is_active = False
        pet.save()
        messages.success(request, f'{pet.name} has been archived.')
        return redirect('pets:list')
    
    context = {
        'pet': pet,
    }
    return render(request, 'pets/delete.html', context)

@login_required
def add_health_record(request, pet_pk):
    """Add health record for a pet"""
    pet = get_object_or_404(Pet, pk=pet_pk, owner=request.user)
    
    if request.method == 'POST':
        form = PetHealthRecordForm(request.POST)
        if form.is_valid():
            health_record = form.save(commit=False)
            health_record.pet = pet
            health_record.save()
            messages.success(request, 'Health record added successfully!')
            return redirect('pets:detail', pk=pet.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PetHealthRecordForm()
    
    context = {
        'form': form,
        'pet': pet,
        'title': f'Add Health Record for {pet.name}',
    }
    return render(request, 'pets/add_health_record.html', context)