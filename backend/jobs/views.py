from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer


class JobListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        jobs = Job.objects.filter(status='active')
        province = request.query_params.get('province')
        contract_type = request.query_params.get('contract_type')
        if province:
            jobs = jobs.filter(province=province)
        if contract_type:
            jobs = jobs.filter(contract_type=contract_type)
        return Response(JobSerializer(jobs, many=True).data)


class JobDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk, status='active')
        return Response(JobSerializer(job).data)


class JobApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applications = JobApplication.objects.filter(nurse__user=request.user)
        return Response(JobApplicationSerializer(applications, many=True).data)

    def post(self, request):
        serializer = JobApplicationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
