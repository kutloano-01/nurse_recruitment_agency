from django.urls import path
from .views import JobListView, JobDetailView, JobApplicationView, AdminJobListView, AdminJobDetailView

urlpatterns = [
    path('', JobListView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),
    path('applications/', JobApplicationView.as_view()),
    path('admin/', AdminJobListView.as_view()),
    path('admin/<int:pk>/', AdminJobDetailView.as_view()),
]
