from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.urls import reverse
from django.contrib import messages
from .models import Encounter, Diagnosis, EncounterDiagnosis, EncounterProcedure
from .forms import EncounterForm, DiagnosisForm, EncounterDiagnosisForm, EncounterProcedureForm 
from django.utils.timezone import now
from appointments.models import Appointments

# ==========================
# Encounter Views
# ==========================
class EncounterListView(LoginRequiredMixin, ListView):
    model = Encounter
    template_name = 'encounters/encounter_list.html'
    context_object_name = 'encounters'
    ordering = ['-encounter_date']
    paginate_by = 10
    login_url = '/admin/login/'




    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get("q", "").strip()
        search_type = self.request.GET.get("search_type", "").strip()
        date = self.request.GET.get("date", "").strip()  

      
        if date:
            queryset = queryset.filter(encounter_date=date)

        
        if not q:
            return queryset

        
        queryset = queryset.annotate(
            patient_full_name=Concat('patient__first_name', Value(" "), 'patient__last_name'),
            doctor_full_name=Concat('doctor__first_name', Value(" "), 'doctor__last_name')
        )

       
        if search_type == "patient":
            queryset = queryset.filter(
                Q(patient__first_name__icontains=q) |
                Q(patient__last_name__icontains=q) |
                Q(patient_full_name__icontains=q)
            )
        elif search_type == "doctor":
            queryset = queryset.filter(
                Q(doctor__first_name__icontains=q) |
                Q(doctor__last_name__icontains=q) |
                Q(doctor_full_name__icontains=q)
            )
        else:
           
            queryset = queryset.filter(
                Q(patient__first_name__icontains=q) |
                Q(patient__last_name__icontains=q) |
                Q(patient_full_name__icontains=q) |
                Q(doctor__first_name__icontains=q) |
                Q(doctor__last_name__icontains=q) |
                Q(doctor_full_name__icontains=q)
            )

        return queryset








class EncounterDetailView(LoginRequiredMixin, DetailView):
    model = Encounter
    template_name = 'encounters/encounter_detail.html'
    context_object_name = 'encounter'
    pk_url_kwarg = 'encounter_id'
    login_url = '/admin/login/'

class EncounterCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request):
        form = EncounterForm()
        return render(request, 'encounters/encounter_form.html', {'form': form, 'title': 'Add Encounter'})

    def post(self, request):
        form = EncounterForm(request.POST)
        if form.is_valid():
            encounter = form.save()
            return redirect('encounters:encounter_detail', encounter_id=encounter.encounter_id)
        return render(request, 'encounters/encounter_form.html', {'form': form, 'title': 'Add Encounter'})

class EncounterUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
        form = EncounterForm(instance=encounter)
        return render(request, 'encounters/encounter_form.html', {'form': form, 'title': 'Edit Encounter'})

    def post(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
        form = EncounterForm(request.POST, instance=encounter)
        if form.is_valid():
            form.save()
            return redirect('encounters:encounter_detail', encounter_id=encounter.encounter_id)
        return render(request, 'encounters/encounter_form.html', {'form': form, 'title': 'Edit Encounter'})

class EncounterDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
        return render(request, 'encounters/encounter_confirm_delete.html', {'encounter': encounter})

    def post(self, request, encounter_id):
        encounter = get_object_or_404(Encounter, encounter_id=encounter_id)
        encounter.delete()
        return redirect('encounters:encounter_list')


# ==========================
# Diagnosis Views
# ==========================
class DiagnosisListView(LoginRequiredMixin, ListView):
    model = Diagnosis
    template_name = 'diagnosis/diagnosis_list.html'
    context_object_name = 'diagnoses'
    ordering = ['name']
    paginate_by = 10
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(name__icontains=query)
            )
        return queryset

class DiagnosisDetailView(LoginRequiredMixin, DetailView):
    model = Diagnosis
    template_name = 'diagnosis/diagnosis_detail.html'
    context_object_name = 'diagnosis'
    pk_url_kwarg = 'diagnosis_id'
    login_url = '/admin/login/'

class DiagnosisCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request):
        form = DiagnosisForm()
        return render(request, 'diagnosis/diagnosis_form.html', {'form': form, 'title': 'Add Diagnosis'})

    def post(self, request):
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            diagnosis = form.save()
            return redirect('encounters:diagnosis_detail', diagnosis_id=diagnosis.diagnosis_id)
        return render(request, 'diagnosis/diagnosis_form.html', {'form': form, 'title': 'Add Diagnosis'})

class DiagnosisUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, diagnosis_id):
        diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)
        form = DiagnosisForm(instance=diagnosis)
        return render(request, 'diagnosis/diagnosis_form.html', {'form': form, 'title': 'Edit Diagnosis'})

    def post(self, request, diagnosis_id):
        diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)
        form = DiagnosisForm(request.POST, instance=diagnosis)
        if form.is_valid():
            form.save()
            return redirect('encounters:diagnosis_detail', diagnosis_id=diagnosis.diagnosis_id)
        return render(request, 'diagnosis/diagnosis_form.html', {'form': form, 'title': 'Edit Diagnosis'})

class DiagnosisDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, diagnosis_id):
        diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)
        related_count = EncounterDiagnosis.objects.filter(diagnosis=diagnosis).count()
        return render(request, 'diagnosis/diagnosis_confirm_delete.html', {
            'diagnosis': diagnosis,
            'related_count': related_count
        })
    
    def post(self, request, diagnosis_id):
        diagnosis = get_object_or_404(Diagnosis, diagnosis_id=diagnosis_id)
        related_count = EncounterDiagnosis.objects.filter(diagnosis=diagnosis).count()
        
        
        confirm = request.POST.get('confirm', 'no')
        if related_count > 0 and confirm != 'yes':
            
            messages.warning(request, f"This diagnosis has {related_count} associated records, deleting them will also delete these data!")
            return redirect('encounters:diagnosis_list')
        
       
        EncounterDiagnosis.objects.filter(diagnosis=diagnosis).delete()
        diagnosis.delete()
        messages.success(request, "Diagnosis and associated records have been deleted")
        return redirect('encounters:diagnosis_list')


# ==========================
# EncounterDiagnosis Views
# ==========================
class EncounterDiagnosisListView(LoginRequiredMixin, ListView):
    model = EncounterDiagnosis
    template_name = 'encounter_diagnosis/encounter_diagnosis_list.html'
    context_object_name = 'encounter_diagnoses'
    paginate_by = 10
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        encounter_id = self.kwargs.get('encounter_id')
        if encounter_id:
            queryset = queryset.filter(encounter__encounter_id=encounter_id)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(diagnosis__code__icontains=query) | Q(diagnosis__name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encounter_id = self.kwargs.get('encounter_id')
        if encounter_id:
            context['encounter'] = get_object_or_404(Encounter, encounter_id=encounter_id)
            context['title'] = f"Encounter {encounter_id} - Diagnoses"
        return context

class EncounterDiagnosisCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, encounter_id=None):
        initial = {}
        if encounter_id:
            initial['encounter'] = get_object_or_404(Encounter, encounter_id=encounter_id)
        form = EncounterDiagnosisForm(initial=initial)
        return render(request, 'encounter_diagnosis/encounter_diagnosis_form.html', {'form': form, 'title': 'Add Diagnosis'})

    def post(self, request, encounter_id=None):
        form = EncounterDiagnosisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('encounters:encounter_diagnosis_list', encounter_id=encounter_id)
        return render(request, 'encounter_diagnosis/encounter_diagnosis_form.html', {'form': form, 'title': 'Add Diagnosis'})

class EncounterDiagnosisUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        encounter_diagnosis = get_object_or_404(EncounterDiagnosis, pk=pk)
        form = EncounterDiagnosisForm(instance=encounter_diagnosis)
        return render(request, 'encounter_diagnosis/encounter_diagnosis_form.html', {'form': form, 'title': 'Edit Diagnosis'})

    def post(self, request, pk):
        encounter_diagnosis = get_object_or_404(EncounterDiagnosis, pk=pk)
        form = EncounterDiagnosisForm(request.POST, instance=encounter_diagnosis)
        if form.is_valid():
            form.save()
            return redirect('encounters:encounter_diagnosis_list', encounter_id=encounter_diagnosis.encounter.encounter_id)
        return render(request, 'encounter_diagnosis/encounter_diagnosis_form.html', {'form': form, 'title': 'Edit Diagnosis'})

class EncounterDiagnosisDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        encounter_diagnosis = get_object_or_404(EncounterDiagnosis, pk=pk)
        return render(request, 'encounter_diagnosis/encounter_diagnosis_confirm_delete.html', {'encounter_diagnosis': encounter_diagnosis})

    def post(self, request, pk):
        encounter_diagnosis = get_object_or_404(EncounterDiagnosis, pk=pk)
        encounter_id = encounter_diagnosis.encounter.encounter_id
        encounter_diagnosis.delete()
        return redirect('encounters:encounter_diagnosis_list', encounter_id=encounter_id)


# ==========================
# EncounterProcedure Views
# ==========================
class EncounterProcedureListView(LoginRequiredMixin, ListView):
    model = EncounterProcedure
    template_name = 'encounter_procedure/encounter_procedure_list.html'
    context_object_name = 'encounter_procedures'
    paginate_by = 10
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        encounter_id = self.kwargs.get('encounter_id')
        if encounter_id:
            queryset = queryset.filter(encounter__encounter_id=encounter_id)
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(procedure__name__icontains=query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encounter_id = self.kwargs.get('encounter_id')
        if encounter_id:
            context['encounter'] = get_object_or_404(Encounter, encounter_id=encounter_id)
            context['title'] = f"Encounter {encounter_id} - Procedures"
        return context

class EncounterProcedureCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, encounter_id=None):
        initial = {}
        if encounter_id:
            initial['encounter'] = get_object_or_404(Encounter, encounter_id=encounter_id)
        form = EncounterProcedureForm(initial=initial)
        return render(request, 'encounter_procedure/encounter_procedure_form.html', {'form': form, 'title': 'Add Procedure'})

    def post(self, request, encounter_id=None):
        form = EncounterProcedureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('encounters:encounter_procedure_list', encounter_id=encounter_id)
        return render(request, 'encounter_procedure/encounter_procedure_form.html', {'form': form, 'title': 'Add Procedure'})

class EncounterProcedureUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        encounter_procedure = get_object_or_404(EncounterProcedure, pk=pk)
        form = EncounterProcedureForm(instance=encounter_procedure)
        return render(request, 'encounter_procedure/encounter_procedure_form.html', {'form': form, 'title': 'Edit Procedure'})

    def post(self, request, pk):
        encounter_procedure = get_object_or_404(EncounterProcedure, pk=pk)
        form = EncounterProcedureForm(request.POST, instance=encounter_procedure)
        if form.is_valid():
            form.save()
            return redirect('encounters:encounter_procedure_list', encounter_id=encounter_procedure.encounter.encounter_id)
        return render(request, 'encounter_procedure/encounter_procedure_form.html', {'form': form, 'title': 'Edit Procedure'})

class EncounterProcedureDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        encounter_procedure = get_object_or_404(EncounterProcedure, pk=pk)
        return render(request, 'encounter_procedure/encounter_procedure_confirm_delete.html', {'encounter_procedure': encounter_procedure})

    def post(self, request, pk):
        encounter_procedure = get_object_or_404(EncounterProcedure, pk=pk)
        encounter_id = encounter_procedure.encounter.encounter_id
        encounter_procedure.delete()
        return redirect('encounters:encounter_procedure_list', encounter_id=encounter_id)



def create_encounter_from_appointment(request, appointment_id):
    """
    Create an Encounter directly from an Appointment,
    then redirect doctor into doctor_dashboard with the encounter opened.
    """

    # 1. Find the appointment
    appt = get_object_or_404(Appointments, pk=appointment_id)

    # 2. Avoid duplicate encounters for SAME patient + SAME date + SAME doctor
    existing = Encounter.objects.filter(
        patient=appt.patient,
        doctor=appt.doctor,
        encounter_date=appt.appointment_date,
    ).first()

    if existing:
        # If exists → redirect to doctor dashboard with this encounter opened
        return redirect(
            f"/doctors/dashboard/?q={appt.patient.mrn}"
            f"&patient_id={appt.patient.pk}"
            f"&encounter_id={existing.encounter_id}"
        )

    # 3. Create a NEW encounter
    encounter = Encounter.objects.create(
        appointment=appt,
        patient=appt.patient,
        doctor=appt.doctor,
        encounter_date=appt.appointment_date,
        visit_type="Consultation",
        notes=None,
    )

    # 4. Redirect doctor into dashboard with this encounter opened
    return redirect(
        f"/doctors/dashboard/?q={appt.patient.mrn}"
        f"&patient_id={appt.patient.pk}"
        f"&encounter_id={encounter.encounter_id}"
    )
