from django.urls import path
from . import views

app_name = 'medical'

urlpatterns = [
    path('vaccinations/', views.vaccination_list, name='vaccination_list'),
    path('vaccinations/add/', views.vaccination_add, name='vaccination_add'),
    path('vaccinations/<int:pk>/', views.vaccination_detail, name='vaccination_detail'),
    path('vaccinations/<int:pk>/edit/', views.vaccination_edit, name='vaccination_edit'),
    path('vaccinations/<int:pk>/delete/', views.vaccination_delete, name='vaccination_delete'),
]