from django.urls import path, include
from . import views, views_api, views_drf


urlpatterns = [
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),

	path('<str:school>/', include([
		path('get-courses/', views.get_courses, name='get_courses'),
		path('add-courses/', views.add_courses, name='add_courses'),

		path('get-rooms/', views.get_rooms, name='get_rooms'),
		path('find-rooms/', views.find_rooms, name='find_rooms'),
	])),

	path('add-courses/', views.add_courses_, name='add_courses_'),
	path('find-rooms/', views.find_rooms_, name='find_rooms_'),

	path('my-courses/', views.my_courses, name='my_courses'),
	path('unsubscribe/<str:unsub_type>/<uuid:unsub_id>/', views.unsubscribe, name='unsubscribe'),

	# My API
	path('api/', views.api_about, name='api_about'),
	path('api/schools/', views_api.schools),
	path('api/<str:school>/', include([
		path('professors/', views_api.professors),
		path('terms/', views_api.terms),
		path('subjects/', views_api.subjects),
		path('courses/', views_api.courses),
		path('sections/', views_api.sections),
	])),

	# DRF
	path('drf/schools/', views_drf.Schools.as_view()),
	path('drf/<str:school>/', include([
		path('professors/', views_drf.Professors.as_view()),
		path('terms/', views_drf.Terms.as_view()),
		path('subjects/', views_drf.Subjects.as_view()),
		path('courses/', views_drf.Courses.as_view()),
		path('sections/', views_drf.Sections.as_view()),
	]))
]
