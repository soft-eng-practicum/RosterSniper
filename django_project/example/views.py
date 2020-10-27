from django.shortcuts import render
from django.urls import path
from django.http import HttpResponse

from example.tasks import add, send_celery_mail

# Create your views here.

def index(request):
    x = add(2, 10)
    text = 'Celery done!' + ' ' + str(x)
    send_celery_mail()
    return HttpResponse(text)


