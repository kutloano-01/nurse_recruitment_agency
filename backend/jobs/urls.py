from django.urls import path
from .views import JobListView, JobDetailView, JobApplicationView

urlpatterns = [
    path('', JobListView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),
    path('applications/', JobApplicationView.as_view()),
]
