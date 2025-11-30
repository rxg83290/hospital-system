# doctors/urls.py

from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [

    # ==========================
    # Doctor Dashboard
    # ==========================
    path("dashboard/", views.doctor_dashboard, name="dashboard"),

    # ==========================
    # Doctors CRUD
    # ==========================
    path("add/", views.DoctorCreateView.as_view(), name="doctor_add"),
    path("<int:doctor_id>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path("<int:doctor_id>/edit/", views.DoctorUpdateView.as_view(), name="doctor_edit"),
    path("<int:doctor_id>/delete/", views.DoctorDeleteView.as_view(), name="doctor_delete"),

    # ==========================
    # Departments CRUD
    # ==========================

    path("departments/add/", views.DepartmentCreateView.as_view(), name="department_add"),
    path("departments/<int:department_id>/", views.DepartmentDetailView.as_view(), name="department_detail"),
    path("departments/<int:department_id>/edit/", views.DepartmentUpdateView.as_view(), name="department_edit"),
    path("departments/<int:department_id>/delete/", views.DepartmentDeleteView.as_view(), name="department_delete"),

    # Department → Doctors List
    path(
        "departments/<int:department_id>/doctors/",
        views.DepartmentDoctorsListView.as_view(),
        name="department_doctors"
    ),
]
