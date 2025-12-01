# doctors/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.urls import reverse
from urllib.parse import urlencode
from pharmacy.models import Procedure1

from .models import Department, Doctors
from .forms import DepartmentForm, DoctorForm

from patients.models import Patients
from encounters.models import Encounter, EncounterProcedure
from pharmacy.models import Medication, Prescription
from billing.models import Bill, BillLine

from django.utils import timezone

from appointments.models import Appointments
from .models import Department, Doctors
from datetime import date
from django.utils import timezone



# ==========================
# Doctor Clinical Dashboard
# (target for role dropdown: "Doctor")
# ==========================



def doctor_dashboard(request):
    """
    Doctor dashboard:
      - Show today's & future appointments
      - Search patient by MRN/name/phone/email
      - Batch add medications & procedures
      - Auto billing for medications + procedures
    """

    # ---------------------------------------------------------
    # 自动计费函数（药物 + 手术）
    # ---------------------------------------------------------
    def sync_billing_for_encounter(encounter):
        bill, _ = Bill.objects.get_or_create(
            encounter=encounter,
            patient=encounter.patient,
            defaults={"status": "PENDING"},
        )

        # 删除旧账单行（避免累积）
        bill.bill_lines.all().delete()

        # ======== 药物明细 ========
        prescriptions = Prescription.objects.filter(encounter=encounter).select_related("medication")
        for p in prescriptions:
            med = p.medication
            qty = max((p.frequency_per_day or 1) * (p.duration_days or 1), 1)

            BillLine.objects.create(
                bill=bill,
                medication=med,
                line_type="MEDICATION",
                quantity=qty,
                unit_price=med.unit_price or 0,
                description1=med.generic_name,
            )

        # ======== 手术 Procedure1 明细 ========
        procedures = EncounterProcedure.objects.filter(encounter=encounter).select_related("procedure")
        for ep in procedures:
            proc = ep.procedure

            BillLine.objects.create(
                bill=bill,
                procedure=proc,
                line_type="PROCEDURE",
                quantity=ep.quantity or 1,
                unit_price=proc.base_price or 0,   # ⚠️ 使用 Procedure1.base_price
                description1=proc.name,
            )

        # ======== 更新总费用 ========
        bill.total_amount = sum(line.calculated_total for line in bill.bill_lines.all())
        bill.save()

        return bill

    # ---------------------------------------------------------
    # 获取 query & POST 参数
    # ---------------------------------------------------------
    query = (request.GET.get("q") or "").strip()
    patient_id = request.GET.get("patient_id") or request.POST.get("patient_id")
    encounter_id = request.GET.get("encounter_id") or request.POST.get("encounter_id")
    action = request.POST.get("action")

    # ---------------------------------------------------------
    # 默认上下文变量
    # ---------------------------------------------------------
    patient = None
    doctor = None
    search_error = None

    today = date.today()
    todays_appointments = []

    encounters = []
    active_encounter = None
    encounter_prescriptions = []
    encounter_bill = None

    medication_options = Medication.objects.none()
    procedure_options = Procedure1.objects.none()

    # ---------------------------------------------------------
    # 1. 获取当前登录医生 doctor_profile
    # ---------------------------------------------------------
    if request.user.is_authenticated and hasattr(request.user, "doctor_profile"):
        doctor = request.user.doctor_profile

    # 加载“今天 + 未来”的预约
    if doctor:
        todays_appointments = (
            Appointments.objects.filter(
                doctor=doctor,
                appointment_date__gte=today
            )
            .select_related("patient")
            .order_by("appointment_date", "start_time")
        )

    # ---------------------------------------------------------
    # 2. 搜索 patient
    # ---------------------------------------------------------
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
        )

        if patients_qs.count() == 0:
            search_error = "No patients found matching your search."
        elif patients_qs.count() == 1:
            patient = patients_qs.first()
        else:
            search_error = "Multiple patients found. Please refine your search."

    # ---------------------------------------------------------
    # 3. POST actions（更新 notes / 添加药物 / 手术 / 删除 / 计费）
    # ---------------------------------------------------------
    if request.method == "POST" and action and patient and encounter_id:

        active_encounter_obj = get_object_or_404(
            Encounter,
            encounter_id=encounter_id,
            patient=patient
        )

        # ======= 修改 Encounter 笔记 =======
        if action == "update_encounter":
            active_encounter_obj.diagnosis_summary = request.POST.get("diagnosis_summary") or None
            active_encounter_obj.treatment_plan = request.POST.get("treatment_plan") or None
            active_encounter_obj.notes = request.POST.get("notes") or None
            active_encounter_obj.save()

        # ======= 添加单个药物 =======
        elif action == "add_prescription":
            med_id = request.POST.get("medication_id")
            dosage = request.POST.get("dosage")
            freq = int(request.POST.get("frequency_per_day") or 1)
            duration = int(request.POST.get("duration_days") or 7)
            instructions = request.POST.get("instructions") or None

            if med_id and dosage:
                med = get_object_or_404(Medication, pk=med_id)
                Prescription.objects.create(
                    encounter=active_encounter_obj,
                    medication=med,
                    dosage=dosage,
                    frequency_per_day=freq,
                    duration_days=duration,
                    instructions=instructions
                )

            sync_billing_for_encounter(active_encounter_obj)

        # ======= 批量添加药物 =======
        elif action == "batch_add_prescriptions":
            meds = request.POST.getlist("medication_id[]")
            dosages = request.POST.getlist("dosage[]")
            freqs = request.POST.getlist("frequency_per_day[]")
            durations = request.POST.getlist("duration_days[]")
            instructions = request.POST.getlist("instructions[]")

            for i in range(len(meds)):
                if meds[i] and dosages[i]:
                    med = Medication.objects.filter(pk=meds[i]).first()
                    if med:
                        Prescription.objects.create(
                            encounter=active_encounter_obj,
                            medication=med,
                            dosage=dosages[i],
                            frequency_per_day=int(freqs[i]),
                            duration_days=int(durations[i]),
                            instructions=instructions[i] or None,
                        )

            sync_billing_for_encounter(active_encounter_obj)

        # ======= 批量添加 Procedure1 手术 =======
        elif action == "batch_add_procedures":
            proc_ids = request.POST.getlist("procedure_id[]")
            quantities = request.POST.getlist("quantity[]")

            for i in range(len(proc_ids)):
                if proc_ids[i]:
                    proc = Procedure1.objects.filter(pk=proc_ids[i]).first()
                    if proc:
                        EncounterProcedure.objects.create(
                            encounter=active_encounter_obj,
                            procedure=proc,
                            quantity=int(quantities[i] or 1),
                        )

            sync_billing_for_encounter(active_encounter_obj)

        # ======= 删除药物 =======
        elif action == "delete_prescription":
            presc_id = request.POST.get("prescription_id")
            Prescription.objects.filter(
                prescription_id=presc_id,
                encounter=active_encounter_obj
            ).delete()

            sync_billing_for_encounter(active_encounter_obj)

        # ======= 手动“同步账单”按钮 =======
        elif action == "sync_billing":
            sync_billing_for_encounter(active_encounter_obj)

        # Redirect 避免重复提交
        base = reverse("doctors:dashboard")
        params = urlencode({
            "q": query,
            "patient_id": patient.pk,
            "encounter_id": encounter_id,
        })
        return redirect(f"{base}?{params}")

    # ---------------------------------------------------------
    # 4. 加载 encounter 数据
    # ---------------------------------------------------------
    if patient:
        encounters = (
            Encounter.objects.filter(patient=patient)
            .select_related("doctor")
            .order_by("-encounter_date", "-created_at")
        )

        active_encounter = encounters.filter(encounter_id=encounter_id).first() if encounter_id else encounters.first()

        if active_encounter:
            encounter_prescriptions = Prescription.objects.filter(encounter=active_encounter)
            encounter_bill = Bill.objects.filter(encounter=active_encounter, patient=patient).first()

        # 药物 & 手术列表
        medication_options = Medication.objects.order_by("generic_name")
        procedure_options = Procedure1.objects.order_by("name")

    # ---------------------------------------------------------
    # 5. 渲染模板
    # ---------------------------------------------------------
    context = {
        "query": query,
        "doctor": doctor,
        "patient": patient,
        "search_error": search_error,

        "today": today,
        "todays_appointments": todays_appointments,

        "encounters": encounters,
        "active_encounter": active_encounter,
        "encounter_prescriptions": encounter_prescriptions,
        "encounter_bill": encounter_bill,

        "medication_options": medication_options,
        "procedure_options": procedure_options,

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
