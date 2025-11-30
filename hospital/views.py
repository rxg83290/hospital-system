# hospital/hospital/views.py

from django.shortcuts import render

def home(request):
    """
    Main homepage view for the Hospital system.
    Renders the home dashboard using the global base.html layout.
    """
    return render(request, "home.html", {"section": "home"})
