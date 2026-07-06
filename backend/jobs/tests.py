from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from accounts.models import User
from nurses.models import NurseProfile
from jobs.models import Job, JobApplication


def make_job(**overrides):
    data = {
        'title': 'ICU Registered Nurse',
        'facility_name': 'Netcare Sunninghill',
        'province': 'GP',
        'city': 'Johannesburg',
        'contract_type': 'full_time',
        'nursing_category': 'registered',
        'salary_display': 'R30 000 – R38 000 pm',
        'description': 'ICU nursing position at a leading private hospital.',
        'status': 'active',
    }
    data.update(overrides)
    return Job.objects.create(**data)


class JobManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@test.com', password='Admin1234!',
            first_name='Admin', last_name='User', role='admin'
        )
        self.nurse = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Thandi', last_name='Mokoena', role='nurse'
        )
        self.employer = User.objects.create_user(
            email='employer@test.com', password='Emp1234!',
            first_name='Sipho', last_name='Dlamini', role='employer'
        )

    def _valid_payload(self, **overrides):
        data = {
            'title': 'Theatre Nurse',
            'facility_name': 'Mediclinic Morningside',
            'province': 'GP',
            'city': 'Sandton',
            'contract_type': 'locum',
            'nursing_category': 'registered',
            'salary_display': 'R280 per hour',
            'description': 'Theatre nursing locum position.',
        }
        data.update(overrides)
        return data

    # ── Create ────────────────────────────────────────────────────────────

    def test_admin_can_create_job(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/jobs/admin/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'Theatre Nurse')
        self.assertEqual(res.data['status'], 'active')

    def test_nurse_cannot_create_job(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.post('/api/jobs/admin/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_create_job(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.post('/api/jobs/admin/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_job(self):
        res = self.client.post('/api/jobs/admin/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_salary_max_less_than_min_rejected(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.post('/api/jobs/admin/', self._valid_payload(
            salary_min='40000', salary_max='30000'
        ), format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('salary_max', res.data)

    # ── Edit ──────────────────────────────────────────────────────────────

    def test_admin_can_edit_job(self):
        job = make_job()
        self.client.force_authenticate(user=self.admin)
        res = self.client.patch(f'/api/jobs/admin/{job.pk}/', {'title': 'Senior ICU Nurse'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Senior ICU Nurse')

    def test_admin_can_change_job_status(self):
        job = make_job()
        self.client.force_authenticate(user=self.admin)
        res = self.client.patch(f'/api/jobs/admin/{job.pk}/', {'status': 'filled'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'filled')

    def test_nurse_cannot_edit_job(self):
        job = make_job()
        self.client.force_authenticate(user=self.nurse)
        res = self.client.patch(f'/api/jobs/admin/{job.pk}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Archive ───────────────────────────────────────────────────────────

    def test_admin_can_archive_job(self):
        job = make_job()
        self.client.force_authenticate(user=self.admin)
        res = self.client.delete(f'/api/jobs/admin/{job.pk}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        job.refresh_from_db()
        self.assertEqual(job.status, 'archived')

    def test_archived_job_excluded_from_admin_list(self):
        make_job(status='archived')
        make_job(title='Active Job')
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/jobs/admin/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'Active Job')

    def test_archived_job_not_in_public_listing(self):
        make_job(status='archived')
        make_job(title='Visible Job')
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'Visible Job')

    # ── Public listing ────────────────────────────────────────────────────

    def test_public_can_list_active_jobs(self):
        make_job()
        make_job(title='Night Shift Nurse', province='WC', city='Cape Town')
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_admin_list_includes_all_non_archived_statuses(self):
        make_job(status='active')
        make_job(status='filled')
        make_job(status='closed')
        make_job(status='archived')
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/jobs/admin/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)


class JobApplicationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.nurse_user = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Thandi', last_name='Mokoena', role='nurse'
        )
        self.nurse_profile = NurseProfile.objects.create(
            user=self.nurse_user,
            id_number='9001015009087',
            phone='0711234567',
            sanc_number='SANC123456',
            nursing_category='registered',
            years_experience=5,
            province='GP',
            city='Johannesburg',
        )
        self.employer = User.objects.create_user(
            email='employer@test.com', password='Emp1234!',
            first_name='Sipho', last_name='Dlamini', role='employer'
        )
        self.job = make_job()
        self.client.force_authenticate(user=self.nurse_user)

    # ── Apply ─────────────────────────────────────────────────────────────

    def test_nurse_can_apply_for_job(self):
        res = self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['job_title'], self.job.title)
        self.assertEqual(res.data['status'], 'applied')

    def test_application_with_cover_note_saves(self):
        res = self.client.post('/api/jobs/applications/', {
            'job': self.job.pk,
            'cover_note': 'I have 5 years ICU experience and am available immediately.'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobApplication.objects.get(pk=res.data['id']).cover_note,
                         'I have 5 years ICU experience and am available immediately.')

    def test_application_stored_in_database(self):
        self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(JobApplication.objects.filter(nurse=self.nurse_profile, job=self.job).count(), 1)

    # ── Duplicate prevention ──────────────────────────────────────────────

    def test_duplicate_application_rejected(self):
        self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        res = self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('job', res.data)

    def test_duplicate_does_not_create_second_record(self):
        self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(JobApplication.objects.filter(nurse=self.nurse_profile, job=self.job).count(), 1)

    # ── Inactive job ──────────────────────────────────────────────────────

    def test_cannot_apply_to_filled_job(self):
        filled_job = make_job(title='Filled Job', status='filled')
        res = self.client.post('/api/jobs/applications/', {'job': filled_job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_apply_to_closed_job(self):
        closed_job = make_job(title='Closed Job', status='closed')
        res = self.client.post('/api/jobs/applications/', {'job': closed_job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── List applications ─────────────────────────────────────────────────

    def test_nurse_can_view_own_applications(self):
        JobApplication.objects.create(nurse=self.nurse_profile, job=self.job)
        res = self.client.get('/api/jobs/applications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['job_title'], self.job.title)

    # ── Permission checks ─────────────────────────────────────────────────

    def test_employer_cannot_apply_for_job(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_apply(self):
        self.client.force_authenticate(user=None)
        res = self.client.post('/api/jobs/applications/', {'job': self.job.pk}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
