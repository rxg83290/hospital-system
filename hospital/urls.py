"""
URL configuration for hospital project.
"""

from django.contrib import admin
from django.urls import path, include
from . import views   # <-- IMPORTANT

urlpatterns = [
    path("", views.home, name="home"),   # homepage
    path('admin/', admin.site.urls),

    path('patients/', include('patients.urls', namespace='patients')),
    path('doctors/', include('doctors.urls', namespace='doctors')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('encounters/', include('encounters.urls', namespace='encounters')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    path('billing/', include('billing.urls', namespace='billing')),
    path('accounts/', include('accounts.urls')),
]
