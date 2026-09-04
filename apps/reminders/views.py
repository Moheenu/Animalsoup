from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Reminders app is working!")
