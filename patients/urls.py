# patients/urls.py
from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [

    # ================================
    # PATIENT DASHBOARD (Auto-load for logged-in patients)
    # ================================
    path("dashboard/", views.patient_dashboard, name="dashboard"),
    path("register/", views.patient_register, name="register"),

    # ================================
    # PATIENT CRUD
    # ================================

    path("add/", views.PatientCreateView.as_view(), name="patient_add"),
    path("<int:patient_id>/", views.PatientDetailView.as_view(), name="patient_detail"),
    path("<int:patient_id>/edit/", views.PatientUpdateView.as_view(), name="patient_edit"),
    path("<int:patient_id>/delete/", views.PatientDeleteView.as_view(), name="patient_delete"),

    # ================================
    # INSURANCE POLICIES (Global list + CRUD)
    # ================================
    
    path("policies/add/", views.InsurancePolicyCreateView.as_view(), name="policy_add"),
    path("policies/<int:policy_id>/", views.InsurancePolicyDetailView.as_view(), name="policy_detail"),
    path("policies/<int:policy_id>/edit/", views.InsurancePolicyUpdateView.as_view(), name="policy_edit"),
    path("policies/<int:policy_id>/delete/", views.InsurancePolicyDeleteView.as_view(), name="policy_delete"),

    # ================================
    # PATIENT-SPECIFIC INSURANCE POLICIES
    # ================================
    path("<int:patient_id>/policies/", views.PatientPolicyListView.as_view(), name="patient_policies"),
]
