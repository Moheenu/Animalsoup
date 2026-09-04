from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('', views.pet_list, name='list'),
    path('add/', views.pet_add, name='add'),
    path('<int:pk>/', views.pet_detail, name='detail'),
    path('<int:pk>/edit/', views.pet_edit, name='edit'),
    path('<int:pk>/delete/', views.pet_delete, name='delete'),
    path('<int:pet_pk>/add-health-record/', views.add_health_record, name='add_health_record'),
]