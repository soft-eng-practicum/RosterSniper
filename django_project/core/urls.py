from django.urls import path
from . import views, views_api, views_drf


urlpatterns = [
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
	path('get-courses/<str:school>/', views.get_courses, name='get_courses'),
	path('add-courses/<str:school>/', views.add_courses, name='add_courses'),
	path('get-rooms/<str:school>/', views.get_rooms, name='get_rooms'),
	path('room-finder/<str:school>/', views.find_rooms, name='find_rooms'),
	path('my-courses/', views.my_courses, name='my_courses'),
	path('unsubscribe/<str:unsub_type>/<uuid:unsub_id>/', views.unsubscribe, name='unsubscribe'),

	# My API
	path('api/schools/', views_api.schools),
	path('api/<str:school>/professors/', views_api.professors),
	path('api/<str:school>/terms/', views_api.terms),
	path('api/<str:school>/subjects/', views_api.subjects),
	path('api/<str:school>/courses/', views_api.courses),
	path('api/<str:school>/sections/', views_api.sections),

	# DRF
	path('drf/schools/', views_drf.Schools.as_view()),
	path('drf/<str:school>/professors/', views_drf.Professors.as_view()),
	path('drf/<str:school>/terms/', views_drf.Terms.as_view()),
	path('drf/<str:school>/subjects/', views_drf.Subjects.as_view()),
	path('drf/<str:school>/courses/', views_drf.Courses.as_view()),
	path('drf/<str:school>/sections/', views_drf.Sections.as_view()),
]
