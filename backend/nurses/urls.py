from django.urls import path
from .views import NurseProfileView, NurseDocumentView, NurseAvailabilityView

urlpatterns = [
    path('profile/', NurseProfileView.as_view()),
    path('documents/', NurseDocumentView.as_view()),
    path('availability/', NurseAvailabilityView.as_view()),
    path('availability/<int:pk>/', NurseAvailabilityView.as_view()),
]
