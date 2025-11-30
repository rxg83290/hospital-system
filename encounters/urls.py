from django.urls import path
from . import views

app_name = 'encounters'

urlpatterns = [
    # ==========================
    # Encounter URLs
    # ==========================

    path('add/', views.EncounterCreateView.as_view(), name='encounter_add'),
    path('<int:encounter_id>/', views.EncounterDetailView.as_view(), name='encounter_detail'),
    path('<int:encounter_id>/edit/', views.EncounterUpdateView.as_view(), name='encounter_edit'),
    path('<int:encounter_id>/delete/', views.EncounterDeleteView.as_view(), name='encounter_delete'),

    # ==========================
    # Diagnosis URLs
    # ==========================

    path('diagnoses/add/', views.DiagnosisCreateView.as_view(), name='diagnosis_add'),
    path('diagnoses/<int:diagnosis_id>/', views.DiagnosisDetailView.as_view(), name='diagnosis_detail'),
    path('diagnoses/<int:diagnosis_id>/edit/', views.DiagnosisUpdateView.as_view(), name='diagnosis_edit'),
    path('diagnoses/<int:diagnosis_id>/delete/', views.DiagnosisDeleteView.as_view(), name='diagnosis_delete'),

    # ==========================
    # EncounterDiagnosis URLs
    # ==========================
    
    path('<int:encounter_id>/diagnoses/add/', views.EncounterDiagnosisCreateView.as_view(), name='encounter_diagnosis_add'),
    path('diagnoses/<int:pk>/edit/', views.EncounterDiagnosisUpdateView.as_view(), name='encounter_diagnosis_edit'),
    path('diagnoses/<int:pk>/delete/', views.EncounterDiagnosisDeleteView.as_view(), name='encounter_diagnosis_delete'),

    # ==========================
    # EncounterProcedure URLs
    # ==========================
    
    path('<int:encounter_id>/procedures/add/', views.EncounterProcedureCreateView.as_view(), name='encounter_procedure_add'),
    path('procedures/<int:pk>/edit/', views.EncounterProcedureUpdateView.as_view(), name='encounter_procedure_edit'),
    path('procedures/<int:pk>/delete/', views.EncounterProcedureDeleteView.as_view(), name='encounter_procedure_delete'),
]
