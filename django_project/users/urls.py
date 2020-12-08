from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


# https://docs.djangoproject.com/en/stable/topics/auth/default/#module-django.contrib.auth.views
urlpatterns = [
	path('register/', views.register, name='register'),
	path('profile/', views.profile, name='profile'),
	path('activate/<uidb64>/<token>/', views.activate, name='activate'),

	path('login/', auth_views.LoginView.as_view(), name='login'),
	path('logout/', auth_views.LogoutView.as_view(), name='logout'),
	path('change-password/',
		views.MyPasswordChangeView.as_view(),
		name='password_change'),
	path('reset-password/request/',
		views.MyPasswordResetView.as_view(),
		name='password_reset'),
	path('reset-password/confirm/<uidb64>/<token>/',
		views.MyPasswordResetConfirmView.as_view(),
		name='password_reset_confirm')
]
