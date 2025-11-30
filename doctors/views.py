# doctors/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.urls import reverse
from urllib.parse import urlencode

from .models import Department, Doctors
from .forms import DepartmentForm, DoctorForm

from patients.models import Patients
from encounters.models import Encounter
from pharmacy.models import Medication, Prescription
from billing.models import Bill, BillLine

from django.utils import timezone

from appointments.models import Appointments
from .models import Department, Doctors



# ==========================
# Doctor Clinical Dashboard
# (target for role dropdown: "Doctor")
# ==========================
def doctor_dashboard(request):
    """
    Doctor-facing dashboard:
      - Search for a patient (name/MRN/phone/email)
      - View all encounters for that patient
      - Edit encounter diagnosis / treatment / notes
      - Add medications (prescriptions) for the active encounter
      - Sync/update billing for that encounter
    """

    query = (request.GET.get("q") or "").strip()

    # IDs from GET or POST
    patient_id = request.GET.get("patient_id") or request.POST.get("patient_id")
    encounter_id = request.GET.get("encounter_id") or request.POST.get("encounter_id")
    action = request.POST.get("action")

    # -----------------------------------
    # Default values to avoid UnboundLocalError
    # -----------------------------------
    patient = None
    search_error = None

    dob = None
    encounters = []
    active_encounter = None
    encounter_prescriptions = []
    encounter_bill = None
    medication_options = Medication.objects.none()

    # --------------------------
    # Resolve patient
    # --------------------------
    if patient_id:
        patient = get_object_or_404(Patients, pk=patient_id)

    elif query:
        patients_qs = Patients.objects.annotate(
            full_name=Concat("first_name", Value(" "), "last_name")
        ).filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(full_name__icontains=query)
            | Q(mrn__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        ).order_by("last_name", "first_name")

        count = patients_qs.count()
        if count == 0:
            search_error = "No patients found matching your search."
        elif count == 1:
            patient = patients_qs.first()
        else:
            search_error = "Multiple patients found. Please refine your search."

    # --------------------------
    # Handle POST actions
    # --------------------------
    if request.method == "POST" and patient and encounter_id and action:

        active_encounter_obj = get_object_or_404(
            Encounter,
            encounter_id=encounter_id,
            patient=patient,
        )

        # 1. Update encounter
        if action == "update_encounter":
            active_encounter_obj.diagnosis_summary = (
                request.POST.get("diagnosis_summary") or ""
            ).strip() or None
            active_encounter_obj.treatment_plan = (
                request.POST.get("treatment_plan") or ""
            ).strip() or None
            active_encounter_obj.notes = (
                request.POST.get("notes") or ""
            ).strip() or None
            active_encounter_obj.save()

        # 2. Add prescription
        elif action == "add_prescription":
            medication_id = request.POST.get("medication_id")
            dosage = (request.POST.get("dosage") or "").strip()
            frequency_per_day = request.POST.get("frequency_per_day") or "1"
            duration_days = request.POST.get("duration_days") or "7"
            instructions = (request.POST.get("instructions") or "").strip() or None

            if medication_id and dosage:
                med = get_object_or_404(Medication, pk=medication_id)
                freq = int(frequency_per_day) if frequency_per_day.isdigit() else 1
                duration = int(duration_days) if duration_days.isdigit() else 7

                Prescription.objects.create(
                    encounter=active_encounter_obj,
                    medication=med,
                    dosage=dosage,
                    frequency_per_day=freq,
                    duration_days=duration,
                    instructions=instructions,
                )

        # 3. Sync billing
        elif action == "sync_billing":

            bill, _created = Bill.objects.get_or_create(
                encounter=active_encounter_obj,
                patient=patient,
                defaults={"status": "PENDING"},
            )

            prescriptions = Prescription.objects.filter(
                encounter=active_encounter_obj
            ).select_related("medication")

            for p in prescriptions:
                med = p.medication
                if not med:
                    continue

                qty = (p.frequency_per_day or 0) * (p.duration_days or 0)
                if qty <= 0:
                    qty = 1

                unit_price = med.unit_price or 0

                BillLine.objects.update_or_create(
                    bill=bill,
                    medication=med,
                    line_type="MEDICATION",
                    defaults={
                        "quantity": qty,
                        "unit_price": unit_price,
                        "description1": med.generic_name,
                    },
                )

            total = sum(line.calculated_total for line in bill.bill_lines.all())
            bill.total_amount = total
            bill.save()

        # Redirect after POST
        base_url = reverse("doctors:dashboard")
        params = {
            "q": query,
            "patient_id": patient.pk,
            "encounter_id": encounter_id,
        }
        return redirect(f"{base_url}?{urlencode(params)}")

    # --------------------------
    # Read-only context
    # --------------------------
    if patient:
        dob = patient.dob

        encounters = (
            Encounter.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-encounter_date", "-created_at")
        )

        active_encounter = (
            encounters.filter(encounter_id=encounter_id).first()
            if encounter_id
            else encounters.first()
        )

        if active_encounter:
            encounter_prescriptions = (
                Prescription.objects.filter(encounter=active_encounter)
                .select_related("medication")
                .order_by("-created_at")
            )
            encounter_bill = (
                Bill.objects.filter(
                    encounter=active_encounter,
                    patient=patient,
                )
                .order_by("-bill_date", "-created_at")
                .first()
            )

        medication_options = Medication.objects.order_by("generic_name")

    # --------------------------
    # Render
    # --------------------------
    context = {
        "query": query,
        "patient": patient,
        "dob": dob,
        "search_error": search_error,
        "encounters": encounters,
        "active_encounter": active_encounter,
        "encounter_prescriptions": encounter_prescriptions,
        "encounter_bill": encounter_bill,
        "medication_options": medication_options,
        "section": "doctors",
    }

    return render(request, "doctors/doctor_dashboard.html", context)


# ==========================
# Department Views
# ==========================
class DepartmentListView(ListView):
    model = Department
    template_name = "departments/department_list.html"
    context_object_name = "departments"
    ordering = ["department_id"]
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = (self.request.GET.get("q") or "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(location__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = (self.request.GET.get("q") or "").strip()
        context["section"] = "doctors"
        return context


class DepartmentDetailView(DetailView):
    model = Department
    template_name = "departments/department_detail.html"
    context_object_name = "department"
    pk_url_kwarg = "department_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # assumes related_name='doctors' on Doctors.department
        context["doctors"] = self.object.doctors.all()
        context["section"] = "doctors"
        return context


class DepartmentCreateView(View):
    def get(self, request):
        form = DepartmentForm()
        return render(request, "departments/department_form.html", {
            "form": form,
            "title": "Add Department",
            "section": "doctors",
        })

    def post(self, request):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            return redirect("doctors:department_detail", department_id=department.department_id)
        return render(request, "departments/department_form.html", {
            "form": form,
            "title": "Add Department",
            "section": "doctors",
        })


class DepartmentUpdateView(View):
    def get(self, request, department_id):
        department = get_object_or_404(Department, department_id=department_id)
        form = DepartmentForm(instance=department)
        return render(request, "departments/department_form.html", {
            "form": form,
            "title": "Edit Department",
            "section": "doctors",
        })

    def post(self, request, department_id):
        department = get_object_or_404(Department, department_id=department_id)
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect("doctors:department_detail", department_id=department.department_id)
        return render(request, "departments/department_form.html", {
            "form": form,
            "title": "Edit Department",
            "section": "doctors",
        })


class DepartmentDeleteView(View):
    def get(self, request, department_id):
        department = get_object_or_404(Department, department_id=department_id)
        return render(request, "departments/department_confirm_delete.html", {
            "department": department,
            "section": "doctors",
        })

    def post(self, request, department_id):
        department = get_object_or_404(Department, department_id=department_id)
        department.delete()
        return redirect("doctors:department_list")


# ==========================
# Doctors Views
# ==========================
class DoctorListView(ListView):
    model = Doctors
    template_name = "doctors/doctor_list.html"
    context_object_name = "doctors"
    ordering = ["last_name", "first_name"]
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = (self.request.GET.get("q") or "").strip()

        if query:
            queryset = queryset.annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            ).filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(specialization__icontains=query) |
                Q(department__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = (self.request.GET.get("q") or "").strip()
        context["section"] = "doctors"
        return context


class DoctorDetailView(DetailView):
    model = Doctors
    template_name = "doctors/doctor_detail.html"
    context_object_name = "doctor"
    pk_url_kwarg = "doctor_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get("next")
        if not next_url and self.object.department:
            # requires get_absolute_url on Department model
            next_url = self.object.department.get_absolute_url()
        context["next_url"] = next_url
        context["section"] = "doctors"
        return context


class DoctorCreateView(View):
    def get(self, request):
        form = DoctorForm()
        return render(request, "doctors/doctor_form.html", {
            "form": form,
            "title": "Add Doctor",
            "section": "doctors",
        })

    def post(self, request):
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            return redirect("doctors:doctor_detail", doctor_id=doctor.doctor_id)
        return render(request, "doctors/doctor_form.html", {
            "form": form,
            "title": "Add Doctor",
            "section": "doctors",
        })


class DoctorUpdateView(View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctors, doctor_id=doctor_id)
        form = DoctorForm(instance=doctor)
        return render(request, "doctors/doctor_form.html", {
            "form": form,
            "title": "Edit Doctor",
            "section": "doctors",
        })

    def post(self, request, doctor_id):
        doctor = get_object_or_404(Doctors, doctor_id=doctor_id)
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect("doctors:doctor_detail", doctor_id=doctor.doctor_id)
        return render(request, "doctors/doctor_form.html", {
            "form": form,
            "title": "Edit Doctor",
            "section": "doctors",
        })


class DoctorDeleteView(View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctors, doctor_id=doctor_id)
        return render(request, "doctors/doctor_confirm_delete.html", {
            "doctor": doctor,
            "section": "doctors",
        })

    def post(self, request, doctor_id):
        doctor = get_object_or_404(Doctors, doctor_id=doctor_id)
        doctor.delete()
        return redirect("doctors:doctor_list")


class DepartmentDoctorsListView(ListView):
    model = Doctors
    template_name = "department_doctors.html"
    context_object_name = "doctors"
    paginate_by = 10

    def get_queryset(self):
        department_id = self.kwargs.get("department_id")
        queryset = Doctors.objects.filter(department__department_id=department_id)

        query = (self.request.GET.get("q") or "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department_id = self.kwargs.get("department_id")
        department = Department.objects.get(department_id=department_id)
        context["department"] = department
        context["title"] = f"Doctors in {department.name}"
        context["section"] = "doctors"
        return context
