from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [

    path('add/', views.AppointmentCreateView.as_view(), name='appointment_add'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='appointment_delete'),

]
