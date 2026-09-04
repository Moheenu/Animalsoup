from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date, timedelta
from .models import Reminder, ReminderLog
from .forms import ReminderForm
from apps.pets.models import Pet

@login_required
def reminder_list(request):
    """View all reminders"""
    
    reminders = Reminder.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('pet')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'pending':
            reminders = reminders.filter(status=Reminder.Status.PENDING)
        elif status_filter == 'completed':
            reminders = reminders.filter(status=Reminder.Status.COMPLETED)
        elif status_filter == 'overdue':
            reminders = reminders.filter(status=Reminder.Status.OVERDUE)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        reminders = reminders.filter(reminder_type=type_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        reminders = reminders.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(reminders, 10)
    page_number = request.GET.get('page')
    reminders = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': Reminder.objects.filter(user=request.user, is_active=True).count(),
        'pending': Reminder.objects.filter(user=request.user, is_active=True, status=Reminder.Status.PENDING).count(),
        'completed': Reminder.objects.filter(user=request.user, is_active=True, status=Reminder.Status.COMPLETED).count(),
        'overdue': Reminder.objects.filter(user=request.user, is_active=True, status=Reminder.Status.OVERDUE).count(),
    }
    
    # Upcoming reminders (next 7 days)
    upcoming_reminders = Reminder.objects.filter(
        user=request.user,
        is_active=True,
        status__in=[Reminder.Status.PENDING],
        reminder_date__gte=date.today(),
        reminder_date__lte=date.today() + timedelta(days=7)
    ).order_by('reminder_date')[:5]
    
    context = {
        'reminders': reminders,
        'stats': stats,
        'upcoming_reminders': upcoming_reminders,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    return render(request, 'reminders/list.html', context)

@login_required
def reminder_add(request):
    """Add a new reminder"""
    
    if request.method == 'POST':
        form = ReminderForm(request.user, request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            
            # Create log entry
            ReminderLog.objects.create(
                reminder=reminder,
                action='CREATED',
                note='Reminder created'
            )
            
            messages.success(request, f'Reminder "{reminder.title}" added successfully!')
            return redirect('reminders:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReminderForm(request.user)
    
    context = {
        'form': form,
        'title': 'Add Reminder',
    }
    return render(request, 'reminders/form.html', context)

@login_required
def reminder_detail(request, pk):
    """View reminder details"""
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    logs = reminder.logs.all()[:10]
    
    context = {
        'reminder': reminder,
        'logs': logs,
    }
    return render(request, 'reminders/detail.html', context)

@login_required
def reminder_edit(request, pk):
    """Edit reminder"""
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ReminderForm(request.user, request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            
            # Create log entry
            ReminderLog.objects.create(
                reminder=reminder,
                action='UPDATED',
                note='Reminder updated'
            )
            
            messages.success(request, f'Reminder "{reminder.title}" updated successfully!')
            return redirect('reminders:detail', pk=reminder.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReminderForm(request.user, instance=reminder)
    
    context = {
        'form': form,
        'reminder': reminder,
        'title': f'Edit {reminder.title}',
    }
    return render(request, 'reminders/form.html', context)

@login_required
def reminder_delete(request, pk):
    """Delete (archive) reminder"""
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        reminder.is_active = False
        reminder.save()
        
        # Create log entry
        ReminderLog.objects.create(
            reminder=reminder,
            action='CANCELLED',
            note='Reminder archived'
        )
        
        messages.success(request, f'Reminder "{reminder.title}" archived successfully!')
        return redirect('reminders:list')
    
    context = {
        'reminder': reminder,
    }
    return render(request, 'reminders/delete.html', context)

@login_required
def reminder_complete(request, pk):
    """Mark reminder as completed"""
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        reminder.status = Reminder.Status.COMPLETED
        reminder.save()
        
        # Create log entry
        ReminderLog.objects.create(
            reminder=reminder,
            action='COMPLETED',
            note='Reminder marked as completed'
        )
        
        messages.success(request, f'Reminder "{reminder.title}" marked as completed!')
        return redirect('reminders:list')
    
    context = {
        'reminder': reminder,
    }
    return render(request, 'reminders/complete.html', context)

@login_required
def reminder_dashboard_widget(request):
    """Widget for dashboard showing upcoming reminders"""
    upcoming = Reminder.objects.filter(
        user=request.user,
        is_active=True,
        status__in=[Reminder.Status.PENDING],
        reminder_date__gte=date.today()
    ).order_by('reminder_date')[:5]
    
    return render(request, 'reminders/dashboard_widget.html', {'upcoming_reminders': upcoming})