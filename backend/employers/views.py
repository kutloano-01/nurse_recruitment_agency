from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.permissions import IsEmployerOrAdmin, IsEmployer
from core.emails import send_employer_registration_confirmation, send_employer_registration_admin_notification
from .models import EmployerProfile, StaffingRequest
from .serializers import EmployerProfileSerializer, StaffingRequestSerializer


class EmployerProfileView(APIView):
    permission_classes = [IsEmployerOrAdmin]

    def get(self, request):
        profile = get_object_or_404(EmployerProfile, user=request.user)
        return Response(EmployerProfileSerializer(profile).data)

    def post(self, request):
        if hasattr(request.user, 'employer_profile'):
            return Response({'error': 'Profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmployerProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save()
            send_employer_registration_confirmation(request.user, profile)
            send_employer_registration_admin_notification(request.user, profile)
            return Response(EmployerProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffingRequestView(APIView):
    permission_classes = [IsEmployer]

    def get(self, request):
        profile = get_object_or_404(EmployerProfile, user=request.user)
        requests = StaffingRequest.objects.filter(employer=profile)
        return Response(StaffingRequestSerializer(requests, many=True).data)

    def post(self, request):
        serializer = StaffingRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
