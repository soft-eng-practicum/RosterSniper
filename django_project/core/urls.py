from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('add-courses/', views.add_courses, name='add_courses'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('unsubscribe/<str:unsubType>/<uuid:unsubID>/', views.unsubscribe, name='unsubscribe'),
]
