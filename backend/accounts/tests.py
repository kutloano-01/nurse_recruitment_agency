from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


class RoleBasedAccessTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email='admin@test.com', password='Admin1234!',
            first_name='Admin', last_name='User', role='admin'
        )
        self.nurse = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Nurse', last_name='User', role='nurse'
        )
        self.employer = User.objects.create_user(
            email='employer@test.com', password='Employer1234!',
            first_name='Employer', last_name='User', role='employer'
        )

    # ── Unauthenticated access ──────────────────────────────────────────

    def test_unauthenticated_cannot_access_nurse_profile(self):
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_employer_profile(self):
        res = self.client.get('/api/employers/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access_job_applications(self):
        res = self.client.get('/api/jobs/applications/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_can_access_job_listings(self):
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ── Nurse access ────────────────────────────────────────────────────

    def test_nurse_cannot_access_employer_profile(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.get('/api/employers/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_nurse_cannot_submit_staffing_request(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.post('/api/employers/requests/', {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_nurse_can_access_own_profile(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.get('/api/nurses/profile/')
        # 404 is acceptable — profile doesn't exist yet but access was granted
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_nurse_can_access_job_listings(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_nurse_can_access_job_applications(self):
        self.client.force_authenticate(user=self.nurse)
        res = self.client.get('/api/jobs/applications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ── Employer access ─────────────────────────────────────────────────

    def test_employer_cannot_access_nurse_profile(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_upload_nurse_documents(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.post('/api/nurses/documents/', {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_set_nurse_availability(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.get('/api/nurses/availability/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_access_job_applications(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.get('/api/jobs/applications/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_can_access_job_listings(self):
        self.client.force_authenticate(user=self.employer)
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ── Admin access ────────────────────────────────────────────────────

    def test_admin_can_access_nurse_profile_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/nurses/profile/')
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_admin_can_access_employer_profile_endpoint(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/employers/profile/')
        self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_admin_can_access_job_listings(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/jobs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_can_access_job_applications(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get('/api/jobs/applications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # ── Auth endpoints ──────────────────────────────────────────────────

    def test_register_returns_201(self):
        res = self.client.post('/api/accounts/register/', {
            'email': 'new@test.com', 'password': 'Test1234!',
            'first_name': 'New', 'last_name': 'User', 'role': 'nurse'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_login_with_valid_credentials(self):
        res = self.client.post('/api/accounts/login/', {
            'email': 'nurse@test.com', 'password': 'Nurse1234!'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_with_invalid_credentials(self):
        res = self.client.post('/api/accounts/login/', {
            'email': 'nurse@test.com', 'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        res = self.client.post('/api/accounts/logout/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
