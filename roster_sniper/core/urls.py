from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('add-course/', views.add_course, name='add_course'),
    path('add-course-2/', views.add_course_2, name='add_course_2'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('unsubscribe/<str:unsubType>/<uuid:unsubID>/', views.unsubscribe),
]
