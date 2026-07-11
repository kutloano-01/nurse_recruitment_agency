from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from core.permissions import IsAdmin
from nurses.models import NurseProfile
from employers.models import EmployerProfile, StaffingRequest
from jobs.models import Job, JobApplication


class AdminStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({
            'nurses': {
                'total': NurseProfile.objects.count(),
                'pending': NurseProfile.objects.filter(status='pending').count(),
                'verified': NurseProfile.objects.filter(status='verified').count(),
                'rejected': NurseProfile.objects.filter(status='rejected').count(),
            },
            'employers': {
                'total': EmployerProfile.objects.count(),
            },
            'jobs': {
                'active': Job.objects.filter(status='active').count(),
                'filled': Job.objects.filter(status='filled').count(),
                'total': Job.objects.exclude(status='archived').count(),
            },
            'applications': {
                'total': JobApplication.objects.count(),
                'applied': JobApplication.objects.filter(status='applied').count(),
                'shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
                'placed': JobApplication.objects.filter(status='placed').count(),
            },
            'staffing_requests': {
                'open': StaffingRequest.objects.filter(status='open').count(),
                'total': StaffingRequest.objects.count(),
            },
        })


class AdminNurseListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        nurses = NurseProfile.objects.select_related('user').order_by('-created_at')
        return Response([{
            'id': n.id,
            'full_name': n.user.get_full_name(),
            'email': n.user.email,
            'sanc_number': n.sanc_number,
            'nursing_category': n.get_nursing_category_display(),
            'province': n.get_province_display(),
            'city': n.city,
            'status': n.status,
            'created_at': n.created_at,
        } for n in nurses])


class AdminNurseDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        nurse = get_object_or_404(NurseProfile, pk=pk)
        new_status = request.data.get('status')
        if new_status not in dict(NurseProfile.STATUS_CHOICES):
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        nurse.status = new_status
        nurse.admin_notes = request.data.get('admin_notes', nurse.admin_notes)
        nurse.save()
        return Response({'id': nurse.id, 'status': nurse.status, 'admin_notes': nurse.admin_notes})


class AdminEmployerListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        employers = EmployerProfile.objects.select_related('user').order_by('-created_at')
        return Response([{
            'id': e.id,
            'facility_name': e.facility_name,
            'facility_type': e.get_facility_type_display(),
            'province': e.get_province_display(),
            'city': e.city,
            'contact_person': e.contact_person,
            'email': e.user.email,
            'phone': e.phone,
            'staffing_requests': e.staffing_requests.count(),
            'created_at': e.created_at,
        } for e in employers])


class AdminJobListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from jobs.serializers import AdminJobSerializer
        jobs = Job.objects.exclude(status='archived').order_by('-created_at')
        data = AdminJobSerializer(jobs, many=True).data
        app_counts = {
            a['job']: a['count']
            for a in JobApplication.objects.values('job').annotate(count=Count('id'))
        }
        for item in data:
            item['application_count'] = app_counts.get(item['id'], 0)
        return Response(data)

    def post(self, request):
        from jobs.serializers import AdminJobSerializer
        serializer = AdminJobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminJobDetailView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        from jobs.serializers import AdminJobSerializer
        job = get_object_or_404(Job, pk=pk)
        serializer = AdminJobSerializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        job.status = 'archived'
        job.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminApplicationListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = JobApplication.objects.select_related('nurse__user', 'job').order_by('-applied_at')
        job_id = request.query_params.get('job')
        if job_id:
            qs = qs.filter(job_id=job_id)
        applications = qs
        return Response([{
            'id': a.id,
            'nurse_name': a.nurse.user.get_full_name(),
            'nurse_email': a.nurse.user.email,
            'job_title': a.job.title,
            'facility': a.job.facility_name,
            'province': a.job.get_province_display(),
            'status': a.status,
            'cover_note': a.cover_note,
            'applied_at': a.applied_at,
        } for a in applications])

    def patch(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk)
        new_status = request.data.get('status')
        if new_status not in dict(JobApplication.STATUS_CHOICES):
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        application.status = new_status
        application.save()
        return Response({'id': application.id, 'status': application.status})
