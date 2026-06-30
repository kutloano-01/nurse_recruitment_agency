from django.urls import path
from .views import EmployerProfileView, StaffingRequestView

urlpatterns = [
    path('profile/', EmployerProfileView.as_view()),
    path('requests/', StaffingRequestView.as_view()),
]
