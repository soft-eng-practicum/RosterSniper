from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('add-courses/', views.add_courses, name='add_courses'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('unsubscribe/<str:unsub_type>/<uuid:unsub_id>/', views.unsubscribe, name='unsubscribe'),
]
