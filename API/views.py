from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def get_view(request):
    return HttpResponse('<h1>Hello get view</h1>')

def post_view(request):
    return HttpResponse('<h1>Hello post view</h1>')
