from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Procedure1, Medication, Prescription
from .forms import Procedure1Form, MedicationForm, PrescriptionForm
from django.urls import reverse
from encounters.models import EncounterProcedure
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

# ==========================
# Procedure Views
# ==========================
class ProcedureListView(LoginRequiredMixin, ListView):
    model = Procedure1
    template_name = 'procedures/procedure_list.html'
    context_object_name = 'procedures'
    ordering = ['name']
    paginate_by = 10
    login_url = '/admin/login/'

class ProcedureDetailView(LoginRequiredMixin, DetailView):
    model = Procedure1
    template_name = 'procedures/procedure_detail.html'
    context_object_name = 'procedure'
    pk_url_kwarg = 'pk'
    login_url = '/admin/login/'

class ProcedureCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request):
        form = Procedure1Form()
        return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Add Procedure'})

    def post(self, request):
        form = Procedure1Form(request.POST)
        if form.is_valid():
            procedure = form.save()
            return redirect('pharmacy:procedure_detail', pk=procedure.pk)
        return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Add Procedure'})

class ProcedureUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure1, pk=pk)
        form = Procedure1Form(instance=procedure)
        return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Edit Procedure'})

    def post(self, request, pk):
        procedure = get_object_or_404(Procedure1, pk=pk)
        form = Procedure1Form(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            return redirect('pharmacy:procedure_detail', pk=procedure.pk)
        return render(request, 'procedures/procedure_form.html', {'form': form, 'title': 'Edit Procedure'})

class ProcedureDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        procedure = get_object_or_404(Procedure1, pk=pk)
        return render(request, 'procedures/procedure_confirm_delete.html', {'procedure': procedure})

    def post(self, request, pk):
        procedure = get_object_or_404(Procedure1, pk=pk)

        # 安全删除：先删除复合主键表中的所有关联
        EncounterProcedure.objects.filter(procedure_id=procedure.procedure_id).delete()

        # 然后删除 Procedure
        procedure.delete()

        return redirect('pharmacy:procedure_list')


# ==========================
# Medication Views
# ==========================
class MedicationListView(LoginRequiredMixin, ListView):
    model = Medication
    template_name = 'procedures/medication_list.html'
    context_object_name = 'medications'
    ordering = ['generic_name']
    paginate_by = 10
    login_url = '/admin/login/'

class MedicationDetailView(LoginRequiredMixin, DetailView):
    model = Medication
    template_name = 'procedures/medication_detail.html'
    context_object_name = 'medication'
    pk_url_kwarg = 'pk'
    login_url = '/admin/login/'

class MedicationCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request):
        form = MedicationForm()
        return render(request, 'procedures/medication_form.html', {'form': form, 'title': 'Add Medication'})

    def post(self, request):
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save()
            return redirect('pharmacy:medication_detail', pk=medication.pk)
        return render(request, 'procedures/medication_form.html', {'form': form, 'title': 'Add Medication'})

class MedicationUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk)
        form = MedicationForm(instance=medication)
        return render(request, 'procedures/medication_form.html', {'form': form, 'title': 'Edit Medication'})

    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk)
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            return redirect('pharmacy:medication_detail', pk=medication.pk)
        return render(request, 'procedures/medication_form.html', {'form': form, 'title': 'Edit Medication'})

class MedicationDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk)
        return render(request, 'procedures/medication_confirm_delete.html', {'medication': medication})

    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk)
        medication.delete()
        return redirect('pharmacy:medication_list')


# ==========================
# Prescription Views
# ==========================
class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = 'procedures/prescription_list.html'
    context_object_name = 'prescriptions'
    ordering = ['prescription_id']
    paginate_by = 10
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = Prescription.objects.select_related(
            'encounter', 'medication'
        ).order_by('prescription_id')

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(prescription_id__icontains=q) |
                Q(encounter__encounter_id__icontains=q) |
                Q(medication__generic_name__icontains=q) |
                Q(dosage__icontains=q)
            )
        return queryset

class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = 'procedures/prescription_detail.html'
    context_object_name = 'prescription'
    pk_url_kwarg = 'pk'
    login_url = '/admin/login/'

class PrescriptionCreateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request):
        form = PrescriptionForm()
        return render(request, 'procedures/prescription_form.html', {'form': form, 'title': 'Add Prescription'})

    def post(self, request):
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save()
            return redirect('pharmacy:prescription_detail', pk=prescription.pk)
        return render(request, 'procedures/prescription_form.html', {'form': form, 'title': 'Add Prescription'})

class PrescriptionUpdateView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        form = PrescriptionForm(instance=prescription)
        return render(request, 'procedures/prescription_form.html', {'form': form, 'title': 'Edit Prescription'})

    def post(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            return redirect('pharmacy:prescription_detail', pk=prescription.pk)
        return render(request, 'procedures/prescription_form.html', {'form': form, 'title': 'Edit Prescription'})

class PrescriptionDeleteView(LoginRequiredMixin, View):
    login_url = '/admin/login/'

    def get(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        return render(request, 'procedures/prescription_confirm_delete.html', {'prescription': prescription})

    def post(self, request, pk):
        prescription = get_object_or_404(Prescription, pk=pk)
        prescription.delete()
        return redirect('pharmacy:prescription_list')
