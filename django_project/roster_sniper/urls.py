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
from django.urls import path, include
from django.views.generic.base import RedirectView

from .error_views import handler418


handler400 = 'roster_sniper.error_views.handler400'
handler403 = 'roster_sniper.error_views.handler403'
handler404 = 'roster_sniper.error_views.handler404'
handler500 = 'roster_sniper.error_views.handler500'

urlpatterns = [
	path('favicon.ico', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
	path('admin/', admin.site.urls),
	path('teapot/', handler418),

	path('', include('core.urls')),
	path('', include('users.urls'))
]
