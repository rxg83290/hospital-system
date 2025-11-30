from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Bill, BillLine, Payment
from django.db.models import Q
from .forms import BillForm, BillLineForm, PaymentForm

# ==========================
# Bill Views
# ==========================
class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 10
    login_url = '/admin/login/'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        search_type = self.request.GET.get('search_type', 'patient')
        if q:
            if search_type == 'patient':
                queryset = queryset.filter(
                    Q(patient__first_name__icontains=q) |
                    Q(patient__last_name__icontains=q)
                )
            elif search_type == 'encounter':
                queryset = queryset.filter(encounter__encounter_id__icontains=q)
        return queryset.order_by('-bill_date')
    

class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    login_url = '/admin/login/'

class BillUpdateView(LoginRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    login_url = '/admin/login/'

class BillDeleteView(LoginRequiredMixin, DeleteView):
    model = Bill
    template_name = 'billing/bill_confirm_delete.html'
    success_url = reverse_lazy('billing:bill_list')
    login_url = '/admin/login/'

class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'billing/bill_detail.html'
    context_object_name = 'bill'
    login_url = '/admin/login/'

# ==========================
# BillLine Views
# ==========================
class BillLineListView(LoginRequiredMixin, ListView):
    model = BillLine
    template_name = 'billing/billline_list.html'
    context_object_name = 'bill_lines'
    paginate_by = 10
    login_url = '/admin/login/'

class BillLineCreateView(LoginRequiredMixin, CreateView):
    model = BillLine
    form_class = BillLineForm
    template_name = 'billing/billline_form.html'
    success_url = reverse_lazy('billing:billline_list')
    login_url = '/admin/login/'

class BillLineUpdateView(LoginRequiredMixin, UpdateView):
    model = BillLine
    form_class = BillLineForm
    template_name = 'billing/billline_form.html'
    success_url = reverse_lazy('billing:billline_list')
    login_url = '/admin/login/'

class BillLineDeleteView(LoginRequiredMixin, DeleteView):
    model = BillLine
    template_name = 'billing/billline_confirm_delete.html'
    success_url = reverse_lazy('billing:billline_list')
    login_url = '/admin/login/'

class BillLineDetailView(LoginRequiredMixin, DetailView):
    model = BillLine
    template_name = 'billing/billline_detail.html'
    context_object_name = 'bill_line'
    login_url = '/admin/login/'

# ==========================
# Payment Views
# ==========================
class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'billing/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    login_url = '/admin/login/'

class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'billing/payment_form.html'
    success_url = reverse_lazy('billing:payment_list')
    login_url = '/admin/login/'

class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'billing/payment_form.html'
    success_url = reverse_lazy('billing:payment_list')
    login_url = '/admin/login/'

class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Payment
    template_name = 'billing/payment_confirm_delete.html'
    success_url = reverse_lazy('billing:payment_list')
    login_url = '/admin/login/'

class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = 'billing/payment_detail.html'
    context_object_name = 'payment'
    login_url = '/admin/login/'
