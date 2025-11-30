from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    # ==========================
    # Procedure URLs
    # ==========================

    path('procedures/add/', views.ProcedureCreateView.as_view(), name='procedure_add'),
    path('procedures/<int:pk>/', views.ProcedureDetailView.as_view(), name='procedure_detail'),
    path('procedures/<int:pk>/edit/', views.ProcedureUpdateView.as_view(), name='procedure_edit'),
    path('procedures/<int:pk>/delete/', views.ProcedureDeleteView.as_view(), name='procedure_delete'),

    # ==========================
    # Medication URLs
    # ==========================

    path('medications/add/', views.MedicationCreateView.as_view(), name='medication_add'),
    path('medications/<int:pk>/', views.MedicationDetailView.as_view(), name='medication_detail'),
    path('medications/<int:pk>/edit/', views.MedicationUpdateView.as_view(), name='medication_edit'),
    path('medications/<int:pk>/delete/', views.MedicationDeleteView.as_view(), name='medication_delete'),

    # ==========================
    # Prescription URLs
    # ==========================
 
    path('prescriptions/add/', views.PrescriptionCreateView.as_view(), name='prescription_add'),
    path('prescriptions/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/<int:pk>/edit/', views.PrescriptionUpdateView.as_view(), name='prescription_edit'),
    path('prescriptions/<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), name='prescription_delete'),
]
