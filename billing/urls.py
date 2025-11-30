from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # ==========================
    # Bill URLs
    # ==========================

    path('bills/add/', views.BillCreateView.as_view(), name='bill_add'),
    path('bills/<int:pk>/', views.BillDetailView.as_view(), name='bill_detail'),
    path('bills/<int:pk>/edit/', views.BillUpdateView.as_view(), name='bill_edit'),
    path('bills/<int:pk>/delete/', views.BillDeleteView.as_view(), name='bill_delete'),

    # ==========================
    # BillLine URLs
    # ==========================

    path('bill_lines/add/', views.BillLineCreateView.as_view(), name='billline_add'),
    path('bill_lines/<int:pk>/', views.BillLineDetailView.as_view(), name='billline_detail'),
    path('bill_lines/<int:pk>/edit/', views.BillLineUpdateView.as_view(), name='billline_edit'),
    path('bill_lines/<int:pk>/delete/', views.BillLineDeleteView.as_view(), name='billline_delete'),

    # ==========================
    # Payment URLs
    # ==========================

    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete/', views.PaymentDeleteView.as_view(), name='payment_delete'),
]

