# accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("signup/doctor/", views.doctor_signup_view, name="doctor_signup")

    # Future (optional)
    # path("logout/", views.logout_view, name="logout"),
]
