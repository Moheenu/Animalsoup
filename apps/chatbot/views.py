from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Chatbot app is working!")
