from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.permissions import IsNurseOrAdmin, IsNurse
from core.emails import send_nurse_registration_confirmation, send_nurse_registration_admin_notification
from .models import NurseProfile, NurseDocument, NurseAvailability
from .serializers import (
    NurseProfileSerializer, NurseRegistrationSerializer,
    NurseProfileUpdateSerializer, NurseDocumentSerializer, NurseAvailabilitySerializer
)


class NurseProfileView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def get(self, request):
        profile = get_object_or_404(NurseProfile, user=request.user)
        return Response(NurseProfileSerializer(profile).data)

    def post(self, request):
        if hasattr(request.user, 'nurse_profile'):
            return Response({'error': 'Profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = NurseRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            profile = serializer.save()
            send_nurse_registration_confirmation(request.user, profile)
            send_nurse_registration_admin_notification(request.user, profile)
            return Response(NurseProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        profile = get_object_or_404(NurseProfile, user=request.user)
        serializer = NurseProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(NurseProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NurseDocumentView(APIView):
    permission_classes = [IsNurse]

    def post(self, request):
        profile = get_object_or_404(NurseProfile, user=request.user)
        serializer = NurseDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(nurse=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NurseAvailabilityView(APIView):
    permission_classes = [IsNurse]

    def get(self, request):
        profile = get_object_or_404(NurseProfile, user=request.user)
        data = NurseAvailabilitySerializer(profile.availability.all(), many=True).data
        return Response(data)

    def post(self, request):
        profile = get_object_or_404(NurseProfile, user=request.user)
        serializer = NurseAvailabilitySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(nurse=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        availability = get_object_or_404(NurseAvailability, pk=pk, nurse__user=request.user)
        availability.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
