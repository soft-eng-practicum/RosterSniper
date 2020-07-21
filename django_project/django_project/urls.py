""" django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic.base import RedirectView

from users import views as user_views

# For sending custom emails:
# https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.PasswordResetView
urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),

    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('activate/<uidb64>/<token>/', user_views.activate, name='activate'),

    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#module-django.contrib.auth.views
    # https://github.com/django/django/blob/master/django/contrib/auth/urls.py

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('change-password/',
        user_views.MyPasswordChangeView.as_view(),
        name='password_change'),
    path('reset-password/request/',
        user_views.MyPasswordResetView.as_view(),
        name='password_reset'),
    path('reset-password/confirm/<uidb64>/<token>/',
        user_views.MyPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    
    path('', include('core.urls')),
]

# docs.djangoproject.com/en/3.0/howto/static-files/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
