from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.home, name='home'),
]
