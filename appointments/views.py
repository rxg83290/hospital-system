from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import Appointments
from .forms import AppointmentForm
from patients.models import Patients


# ==========================
# Appointments Views
# ==========================

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointments
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"
    ordering = ["appointment_date", "start_time"]
    paginate_by = 10
    login_url = "/admin/login/"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("q", "")

        if search_query:
            queryset = queryset.filter(
                Q(patient__mrn__icontains=search_query)
                | Q(patient__first_name__icontains=search_query)
                | Q(patient__last_name__icontains=search_query)
                | Q(doctor__first_name__icontains=search_query)
                | Q(doctor__last_name__icontains=search_query)
                | Q(doctor__specialization__icontains=search_query)
                | Q(appointment_date__icontains=search_query)
            )

        return queryset


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointments
    template_name = "appointments/appointment_detail.html"
    context_object_name = "appointment"
    pk_url_kwarg = "pk"
    login_url = "/admin/login/"


class AppointmentCreateView(LoginRequiredMixin, View):
    login_url = "/admin/login/"

    def _get_patient_for_user(self, user):
        """
        Ensure the logged-in user is a patient and fetch their patient record.
        """
        if getattr(user, "role", None) != "patient":
            raise PermissionDenied("Only patient accounts can book appointments.")
        return get_object_or_404(Patients, user=user)

    def get(self, request):
        patient = self._get_patient_for_user(request.user)
        form = AppointmentForm(patient=patient)
        return render(request, "appointments/appointment_form.html", {
            "form": form,
            "title": "Add Appointment",
        })

    def post(self, request):
        patient = self._get_patient_for_user(request.user)
        form = AppointmentForm(request.POST, patient=patient)
        if form.is_valid():
            appointment = form.save()
            # After creating: show the appointment detail
            return redirect("appointments:appointment_detail", pk=appointment.pk)
        return render(request, "appointments/appointment_form.html", {
            "form": form,
            "title": "Add Appointment",
        })


class AppointmentUpdateView(LoginRequiredMixin, View):
    login_url = "/admin/login/"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointments, pk=pk)

        # IMPORTANT: pass patient=appointment.patient
        form = AppointmentForm(
            instance=appointment,
            patient=appointment.patient,
        )

        return render(request, "appointments/appointment_form.html", {
            "form": form,
            "title": "Edit Appointment",
        })

    def post(self, request, pk):
        appointment = get_object_or_404(Appointments, pk=pk)

        # IMPORTANT: pass patient=appointment.patient
        form = AppointmentForm(
            request.POST,
            instance=appointment,
            patient=appointment.patient,
        )

        if form.is_valid():
            form.save()
            # After editing: go back to the appointment detail
            return redirect("appointments:appointment_detail", pk=appointment.pk)

        return render(request, "appointments/appointment_form.html", {
            "form": form,
            "title": "Edit Appointment",
        })


class AppointmentDeleteView(LoginRequiredMixin, View):
    login_url = "/admin/login/"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointments, pk=pk)
        return render(request, "appointments/appointment_confirm_delete.html", {
            "appointment": appointment,
        })

    def post(self, request, pk):
        appointment = get_object_or_404(Appointments, pk=pk)
        appointment.delete()
        # After deleting: send patient back to their dashboard
        return redirect("patients:dashboard")
