# patients/admin.py
from django.contrib import admin
from .models import Department, Doctors

admin.site.register(Department)

@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'department', 'user')
    search_fields = ('first_name', 'last_name')