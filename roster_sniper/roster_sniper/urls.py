""" roster_sniper URL Configuration

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from users import views as user_views

# For sending custom emails:
# https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.PasswordResetView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            user_views.activate, name='activate'),
    path('login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'),
    path('logout/',
        auth_views.LogoutView.as_view(template_name='logout.html'),
        name='logout'),
    path('password-reset/request/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset/request.html'),
        name='password_reset'),
    path('password-reset/sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset/sent.html'),
        name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset/confirm.html'),
        name='password_reset_confirm'),
    path('password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset/complete.html'),
        name='password_reset_complete'),
    path('', include('core.urls')),
]

# docs.djangoproject.com/en/3.0/howto/static-files/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
