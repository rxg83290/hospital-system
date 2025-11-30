# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login

from .models import CustomUser   # make sure this import is present
from doctors.models import Doctors   # ⬅️ ADDED for welcome message


# ==========================================
# LOGIN VIEW
# ==========================================
def login_view(request):
    """
    Handles user login using username, password, and selected role.
    Ensures the selected role matches the role assigned to the user.
    Redirects to the correct dashboard after successful login.
    """

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "")

        # Validation
        if not username or not password or not role:
            messages.error(request, "Please enter your username, password, and select a role.")
            return render(request, "accounts/login.html")

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid username or password.")
            return render(request, "accounts/login.html")

        # Ensure the chosen role matches the user account's role
        if hasattr(user, "role") and user.role != role:
            messages.error(
                request,
                "You selected the wrong role. Please choose the correct role assigned to your account."
            )
            return render(request, "accounts/login.html")

        # Login
        login(request, user)

        # Redirect by role
        if role == "patient":
            return redirect("patients:dashboard")

        if role == "doctor":
            # ⬅️ NEW: Doctor welcome message
            doctor = Doctors.objects.filter(user=user).first()

            if doctor:
                full_name = f"{doctor.first_name} {doctor.last_name}"
                messages.success(request, f"Welcome, Dr. {full_name}!")
            else:
                full_name = user.get_full_name() or user.username
                messages.success(request, f"Welcome, {full_name}!")

            return redirect("doctors:dashboard")

        if role == "nurse":
            messages.info(request, "The Nurse dashboard is coming soon.")
            return redirect("patients:dashboard")

        if role == "billing":
            messages.info(request, "The Billing dashboard is coming soon.")
            return redirect("patients:dashboard")

        if role == "admin":
            messages.info(request, "The Admin dashboard is coming soon.")
            return redirect("patients:dashboard")

        # Fallback
        messages.error(request, "Invalid role selected.")
        return render(request, "accounts/login.html")

    # GET → Show form
    return render(request, "accounts/login.html")


# ==========================================
# SIGNUP VIEW (Role Selection)
# ==========================================
def signup_view(request):
    """
    Allows the user to choose which role they want to register as.
    Redirects to the correct registration form.
    """
    if request.method == "POST":
         return redirect("patients:register")

    # GET → Show form
    return render(request, "accounts/signup.html")

    '''
# ==========================================
# DOCTOR SIGNUP VIEW
# ==========================================
def doctor_signup_view(request):
    """
    Self-registration for doctors.
    Creates a CustomUser with role='doctor'.
    You can later attach a Doctor profile model if needed.
    """
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        errors = []

        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        # Username uniqueness
        if username and CustomUser.objects.filter(username=username).exists():
            errors.append("That username is already taken. Please choose another.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, "accounts/doctor_signup_form.html")

        # Create the doctor user
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email or "",
            role="doctor",
        )

        messages.success(
            request,
            "Your doctor account has been created successfully. "
            "You can now sign in with your username and password."
        )
        return redirect("accounts:login")

    # GET -> show empty form
    return render(request, "accounts/doctor_signup_form.html")
    '''

def doctor_signup_view(request):
    """
    Doctor self-signup is disabled. Doctors must be created by admin.
    """
    messages.error(request, "Doctors cannot self-register. Please contact the administrator.")
    return redirect("accounts:login")   