from django.urls import path
from . import views

app_name = 'veterinarians'

urlpatterns = [
    path('', views.home, name='home'),
]
