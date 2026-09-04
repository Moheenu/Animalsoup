from django.urls import path
from . import views

app_name = 'medical'

urlpatterns = [
    path('', views.home, name='home'),
]
