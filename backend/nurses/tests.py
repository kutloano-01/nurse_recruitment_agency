from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from nurses.models import NurseProfile, NurseAvailability


class NurseProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.nurse_user = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Thandi', last_name='Mokoena', role='nurse'
        )
        self.profile = NurseProfile.objects.create(
            user=self.nurse_user,
            id_number='9001015009087',
            phone='0711234567',
            sanc_number='SANC123456',
            nursing_category='registered',
            speciality='ICU',
            years_experience=5,
            province='GP',
            city='Johannesburg',
        )
        self.client.force_authenticate(user=self.nurse_user)

    # ── Display profile ──────────────────────────────────────────────────

    def test_profile_displays_correctly(self):
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['full_name'], 'Thandi Mokoena')
        self.assertEqual(res.data['first_name'], 'Thandi')
        self.assertEqual(res.data['last_name'], 'Mokoena')
        self.assertEqual(res.data['email'], 'nurse@test.com')
        self.assertEqual(res.data['sanc_number'], 'SANC123456')
        self.assertEqual(res.data['province'], 'GP')
        self.assertEqual(res.data['city'], 'Johannesburg')
        self.assertIn('documents', res.data)
        self.assertIn('availability', res.data)

    def test_profile_includes_status(self):
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.data['status'], 'pending')

    # ── Update personal details ──────────────────────────────────────────

    def test_update_city_saves_correctly(self):
        res = self.client.patch('/api/nurses/profile/', {'city': 'Cape Town'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['city'], 'Cape Town')

    def test_update_phone_saves_correctly(self):
        res = self.client.patch('/api/nurses/profile/', {'phone': '0829876543'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['phone'], '0829876543')

    def test_update_speciality_saves_correctly(self):
        res = self.client.patch('/api/nurses/profile/', {'speciality': 'Theatre'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['speciality'], 'Theatre')

    def test_update_first_name_saves_correctly(self):
        res = self.client.patch('/api/nurses/profile/', {'first_name': 'Nomsa'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.nurse_user.refresh_from_db()
        self.assertEqual(self.nurse_user.first_name, 'Nomsa')

    def test_update_email_saves_correctly(self):
        res = self.client.patch('/api/nurses/profile/', {'email': 'new@test.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.nurse_user.refresh_from_db()
        self.assertEqual(self.nurse_user.email, 'new@test.com')

    # ── Validation ───────────────────────────────────────────────────────

    def test_invalid_phone_rejected(self):
        res = self.client.patch('/api/nurses/profile/', {'phone': '123'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', res.data)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            email='taken@test.com', password='Pass1234!',
            first_name='Other', last_name='User', role='nurse'
        )
        res = self.client.patch('/api/nurses/profile/', {'email': 'taken@test.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Availability ─────────────────────────────────────────────────────

    def test_add_availability_succeeds(self):
        res = self.client.post('/api/nurses/availability/', {
            'day': 'mon', 'shift': 'day'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_availability_returns_list(self):
        NurseAvailability.objects.create(nurse=self.profile, day='mon', shift='day')
        NurseAvailability.objects.create(nurse=self.profile, day='wed', shift='night')
        res = self.client.get('/api/nurses/availability/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_delete_availability_succeeds(self):
        avail = NurseAvailability.objects.create(nurse=self.profile, day='fri', shift='day')
        res = self.client.delete(f'/api/nurses/availability/{avail.pk}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NurseAvailability.objects.filter(pk=avail.pk).count(), 0)

    def test_duplicate_availability_rejected(self):
        NurseAvailability.objects.create(nurse=self.profile, day='mon', shift='day')
        res = self.client.post('/api/nurses/availability/', {
            'day': 'mon', 'shift': 'day'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Permission checks ────────────────────────────────────────────────

    def test_employer_cannot_view_nurse_profile(self):
        employer = User.objects.create_user(
            email='emp@test.com', password='Emp1234!',
            first_name='Emp', last_name='User', role='employer'
        )
        self.client.force_authenticate(user=employer)
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_view_profile(self):
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/nurses/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
