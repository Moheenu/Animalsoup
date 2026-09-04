from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.reminder_list, name='list'),
    path('add/', views.reminder_add, name='add'),
    path('<int:pk>/', views.reminder_detail, name='detail'),
    path('<int:pk>/edit/', views.reminder_edit, name='edit'),
    path('<int:pk>/delete/', views.reminder_delete, name='delete'),
    path('<int:pk>/complete/', views.reminder_complete, name='complete'),
    path('dashboard-widget/', views.reminder_dashboard_widget, name='dashboard_widget'),
]