from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from accounts.models import CustomUser
from .models import Patients, InsurancePolicy
from .forms import PatientForm, InsurancePolicyForm
from appointments.models import Appointments
from encounters.models import Encounter
from billing.models import Bill
from pharmacy.models import Prescription


# ==========================
# Patient Self-Registration
# ==========================

@transaction.atomic
def patient_register(request):
    """
    Public patient registration:
    - Collects basic demographics + login credentials.
    - Creates CustomUser with role='patient'.
    - Assigns the next available MRN, starting at MRN101.
    - Creates Patients record linked to that user.
    - Shows the MRN in a success message and redirects to login.
    """
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        dob_str = request.POST.get("dob", "").strip()
        sex = request.POST.get("sex", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        address = request.POST.get("address", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        errors = []

        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not dob_str:
            errors.append("Date of birth is required.")
        if sex not in ["M", "F"]:
            errors.append("Please select a valid sex.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        # Phone
        if phone:
            if len(phone) > 10 or len(phone) < 10:
                errors.append("Phone is invalid, please enter 10 digits")
            elif not phone.isdigit():
                errors.append("Phone is invalid, please enter 10 digits")

        # Parse DOB
        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Date of birth format is invalid.")

        # Username uniqueness
        if username and CustomUser.objects.filter(username=username).exists():
            errors.append("That username is already taken. Please choose another.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "patients/patients_register.html")

        # ==========================
        # Generate next MRN (MRN101+)
        # ==========================
        # MRN format: "MRN<number>"
        # MRN1–MRN100 are considered already taken; new ones start from MRN101.
        existing_mrns = (
            Patients.objects
            .select_for_update()
            .filter(mrn__startswith="MRN")
            .values_list("mrn", flat=True)
        )

        max_num = 100  # so the first new one becomes MRN101
        for mrn in existing_mrns:
            suffix = mrn.replace("MRN", "")
            if suffix.isdigit():
                n = int(suffix)
                if n > max_num:
                    max_num = n

        next_num = max_num + 1
        new_mrn = f"MRN{next_num}"

        # ==========================
        # Create user
        # ==========================
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email or "",
            role="patient",
        )

        # ==========================
        # Create patient linked to user
        # ==========================
        patient = Patients.objects.create(
            user=user,
            mrn=new_mrn,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
            sex=sex,
            phone=phone or None,
            email=email or None,
            address=address or None,
        )

        messages.success(
            request,
            f"Your account has been created successfully. "
            f"Your Medical Record Number (MRN) is {patient.mrn}. "
            "Please keep it for your records and sign in using your username and password."
        )
        return redirect("accounts:login")

    # GET → show empty registration form
    return render(request, "patients/patients_register.html")


# ==========================
# Patient Dashboard
# ==========================

@login_required
def patient_dashboard(request):
    """
    Patient dashboard.

    - If the logged-in user is a PATIENT, automatically load
      the Patients record linked to request.user and show THEIR data.
    - For other roles (e.g., doctor/admin), keep the search behavior:
      /patients/dashboard/?q=<mrn/name/phone/email>
    """

    user = request.user

    patient = None
    search_error = None
    query = ""

    upcoming_appointments = []
    recent_encounters = []
    recent_bills = []
    recent_medications = []

    # -----------------------------------------
    # (A) PATIENT USER → auto-load own record
    # -----------------------------------------
    if getattr(user, "role", None) == "patient":
        try:
            patient = Patients.objects.get(user=user)
        except Patients.DoesNotExist:
            search_error = (
                "No patient record is linked to your account. "
                "Please contact the clinic to complete your registration."
            )

    # -----------------------------------------
    # (B) NON-PATIENT USER → keep search behavior
    # -----------------------------------------
    else:
        query = request.GET.get("q", "").strip()

        if query:
            patient_qs = Patients.objects.filter(
                Q(mrn__iexact=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(phone__icontains=query)
                | Q(email__icontains=query)
            )
            patient = patient_qs.first()

            if not patient:
                search_error = "No patient found matching that search."

    # -----------------------------------------
    # (C) If we have a patient → load dashboard data
    # -----------------------------------------
    primary_insurance = None 

    if patient:
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()


        primary_insurance = patient.policies.filter(is_primary=True).first()
       

        # Upcoming appointments
        upcoming_appointments = (
            Appointments.objects.filter(patient=patient)
            .filter(
                Q(appointment_date__gt=today)
                | Q(appointment_date=today, start_time__gte=current_time)
            )
            .exclude(status__in=["CANCELLED", "NO_SHOW"])
            .order_by("appointment_date", "start_time")[:5]
        )

        # Recent encounters
        recent_encounters = (
            Encounter.objects.filter(patient=patient)
            .order_by("-encounter_date")[:5]
        )

        # Recent bills
        recent_bills = (
            Bill.objects.filter(patient=patient)
            .order_by("-bill_date", "-bill_id")[:5]
        )

        # Recent medications
        recent_medications = (
            Prescription.objects.filter(encounter__patient=patient)
            .select_related("medication")
            .order_by("-created_at")[:5]
        )

    # -----------------------------------------
    # (D) Send all data to template
    # -----------------------------------------
    context = {
        "query": query,
        "search_error": search_error,
        "patient": patient,
        "primary_insurance": primary_insurance,   
        "upcoming_appointments": upcoming_appointments,
        "recent_encounters": recent_encounters,
        "recent_bills": recent_bills,
        "recent_medications": recent_medications,
    }

    return render(request, "patients/patient_dashboard.html", context)


# ==========================
# Patient CRUD Views
# ==========================

class PatientDetailView(DetailView):
    model = Patients
    template_name = "patients/patient_detail.html"
    context_object_name = "patient"
    pk_url_kwarg = "patient_id"


class PatientCreateView(View):
    def get(self, request):
        form = PatientForm()
        return render(request, "patients/patient_form.html", {
            "form": form,
            "title": "Add Patient",
            "section": "patients",
        })

    def post(self, request):
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return redirect("patients:patient_detail", patient_id=patient.patient_id)
        return render(request, "patients/patient_form.html", {
            "form": form,
            "title": "Add Patient",
            "section": "patients",
        })


class PatientUpdateView(View):
    def get(self, request, patient_id):
        patient = get_object_or_404(Patients, patient_id=patient_id)
        form = PatientForm(instance=patient)
        return render(request, "patients/patient_form.html", {
            "form": form,
            "title": "Edit Patient",
            "section": "patients",
        })

    def post(self, request, patient_id):
        patient = get_object_or_404(Patients, patient_id=patient_id)
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect("patients:patient_detail", patient_id=patient.patient_id)
        return render(request, "patients/patient_form.html", {
            "form": form,
            "title": "Edit Patient",
            "section": "patients",
        })


class PatientDeleteView(View):
    def get(self, request, patient_id):
        patient = get_object_or_404(Patients, patient_id=patient_id)
        return render(request, "patients/patient_confirm_delete.html", {
            "patient": patient,
            "section": "patients",
        })

    def post(self, request, patient_id):
        patient = get_object_or_404(Patients, patient_id=patient_id)
        patient.delete()
        return redirect("patients:patient_list")


class PatientListView(ListView):
    model = Patients
    template_name = "patients/patient_list.html"
    context_object_name = "patients"


# ==========================
# InsurancePolicy Views
# ==========================

class InsurancePolicyListView(ListView):
    model = InsurancePolicy
    template_name = "insurance/policy_list.html"
    context_object_name = "policies"
    ordering = ["patient", "payer_name"]
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        patient_id = self.kwargs.get("patient_id")

        if patient_id:
            queryset = queryset.filter(patient__patient_id=patient_id)

        if query:
            queryset = queryset.annotate(
                full_name=Concat("patient__first_name", Value(" "), "patient__last_name")
            ).filter(
                Q(policy_number__icontains=query)
                | Q(payer_name__icontains=query)
                | Q(plan_name__icontains=query)
                | Q(patient__first_name__icontains=query)
                | Q(patient__last_name__icontains=query)
                | Q(full_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get("patient_id")
        if patient_id:
            patient = Patients.objects.get(patient_id=patient_id)
            context["patient"] = patient
            context["title"] = f"{patient.first_name} {patient.last_name} - Policies"
        context["section"] = "patients"
        return context


class InsurancePolicyDetailView(DetailView):
    model = InsurancePolicy
    template_name = "insurance/policy_detail.html"
    context_object_name = "policy"
    pk_url_kwarg = "policy_id"


class InsurancePolicyCreateView(View):
    def get(self, request):
        patient_id = request.GET.get("patient_id")
        next_url = request.GET.get("next", "/patients/policies/")
        initial = {}

        if patient_id:
            initial["patient"] = get_object_or_404(Patients, patient_id=patient_id)

        form = InsurancePolicyForm(initial=initial)
        return render(request, "insurance/policy_form.html", {
            "form": form,
            "title": "Add Insurance Policy",
            "next": next_url,
            "section": "patients",
        })

    def post(self, request):
        next_url = request.POST.get("next", "/patients/policies/")
        form = InsurancePolicyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(next_url)
        return render(request, "insurance/policy_form.html", {
            "form": form,
            "title": "Add Insurance Policy",
            "next": next_url,
            "section": "patients",
        })


class InsurancePolicyUpdateView(View):
    def get(self, request, policy_id):
        policy = get_object_or_404(InsurancePolicy, policy_id=policy_id)
        next_url = request.GET.get("next", "/patients/policies/")
        form = InsurancePolicyForm(instance=policy)
        return render(request, "insurance/policy_form.html", {
            "form": form,
            "title": "Edit Insurance Policy",
            "next": next_url,
            "section": "patients",
        })

    def post(self, request, policy_id):
        policy = get_object_or_404(InsurancePolicy, policy_id=policy_id)
        next_url = request.POST.get("next", "/patients/policies/")
        form = InsurancePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            return redirect(next_url)
        return render(request, "insurance/policy_form.html", {
            "form": form,
            "title": "Edit Insurance Policy",
            "next": next_url,
            "section": "patients",
        })


class InsurancePolicyDeleteView(View):
    def get(self, request, policy_id):
        policy = get_object_or_404(InsurancePolicy, policy_id=policy_id)
        next_url = request.GET.get("next", "/patients/policies/")
        return render(request, "insurance/policy_confirm_delete.html", {
            "policy": policy,
            "next": next_url,
            "section": "patients",
        })

    def post(self, request, policy_id):
        policy = get_object_or_404(InsurancePolicy, policy_id=policy_id)
        next_url = request.POST.get("next", "/patients/policies/")
        policy.delete()
        return redirect(next_url)


class PatientPolicyListView(ListView):
    model = InsurancePolicy
    template_name = "insurance/policy_list.html"
    context_object_name = "policies"
    paginate_by = 10

    def get_queryset(self):
        patient_id = self.kwargs.get("patient_id")
        return InsurancePolicy.objects.filter(patient__patient_id=patient_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get("patient_id")
        patient = Patients.objects.get(patient_id=patient_id)
        context["patient"] = patient
        context["title"] = f"{patient.first_name} {patient.last_name} - Policies"
        context["section"] = "patients"
        return context
