import datetime
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from accounts.models import User
from employers.models import EmployerProfile, StaffingRequest


class EmployerProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.employer_user = User.objects.create_user(
            email='employer@test.com', password='Emp1234!',
            first_name='Sipho', last_name='Dlamini', role='employer'
        )
        self.profile = EmployerProfile.objects.create(
            user=self.employer_user,
            facility_name='Netcare Sunninghill',
            facility_type='private_hospital',
            province='GP',
            city='Johannesburg',
            address='25 Nanyuki Road, Sunninghill',
            contact_person='Sipho Dlamini',
            phone='0112345678',
        )
        self.client.force_authenticate(user=self.employer_user)

    # ── Display profile ──────────────────────────────────────────────────

    def test_profile_displays_correctly(self):
        res = self.client.get('/api/employers/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['facility_name'], 'Netcare Sunninghill')
        self.assertEqual(res.data['facility_type'], 'private_hospital')
        self.assertEqual(res.data['province'], 'GP')
        self.assertEqual(res.data['city'], 'Johannesburg')
        self.assertEqual(res.data['phone'], '0112345678')

    # ── Create profile ───────────────────────────────────────────────────

    def test_duplicate_profile_rejected(self):
        res = self.client.post('/api/employers/profile/', {
            'facility_name': 'Another Facility',
            'facility_type': 'clinic',
            'province': 'WC',
            'city': 'Cape Town',
            'address': '1 Main Road',
            'contact_person': 'Sipho Dlamini',
            'phone': '0219876543',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Validation ───────────────────────────────────────────────────────

    def test_short_facility_name_rejected(self):
        new_user = User.objects.create_user(
            email='new@test.com', password='Pass1234!',
            first_name='New', last_name='User', role='employer'
        )
        self.client.force_authenticate(user=new_user)
        res = self.client.post('/api/employers/profile/', {
            'facility_name': 'AB',
            'facility_type': 'clinic',
            'province': 'WC',
            'city': 'Cape Town',
            'address': '1 Main Road',
            'contact_person': 'New User',
            'phone': '0219876543',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('facility_name', res.data)

    def test_invalid_phone_rejected(self):
        new_user = User.objects.create_user(
            email='new2@test.com', password='Pass1234!',
            first_name='New', last_name='User', role='employer'
        )
        self.client.force_authenticate(user=new_user)
        res = self.client.post('/api/employers/profile/', {
            'facility_name': 'Valid Facility',
            'facility_type': 'clinic',
            'province': 'WC',
            'city': 'Cape Town',
            'address': '1 Main Road',
            'contact_person': 'New User',
            'phone': '123',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', res.data)

    def test_short_address_rejected(self):
        new_user = User.objects.create_user(
            email='new3@test.com', password='Pass1234!',
            first_name='New', last_name='User', role='employer'
        )
        self.client.force_authenticate(user=new_user)
        res = self.client.post('/api/employers/profile/', {
            'facility_name': 'Valid Facility',
            'facility_type': 'clinic',
            'province': 'WC',
            'city': 'Cape Town',
            'address': '1 Rd',
            'contact_person': 'New User',
            'phone': '0219876543',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('address', res.data)

    # ── Permission checks ────────────────────────────────────────────────

    def test_nurse_cannot_view_employer_profile(self):
        nurse = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Thandi', last_name='Mokoena', role='nurse'
        )
        self.client.force_authenticate(user=nurse)
        res = self.client.get('/api/employers/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_view_profile(self):
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/employers/profile/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StaffingRequestTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.employer_user = User.objects.create_user(
            email='employer@test.com', password='Emp1234!',
            first_name='Sipho', last_name='Dlamini', role='employer'
        )
        self.profile = EmployerProfile.objects.create(
            user=self.employer_user,
            facility_name='Netcare Sunninghill',
            facility_type='private_hospital',
            province='GP',
            city='Johannesburg',
            address='25 Nanyuki Road, Sunninghill',
            contact_person='Sipho Dlamini',
            phone='0112345678',
        )
        self.client.force_authenticate(user=self.employer_user)
        self.tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        self.next_week = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()

    def _valid_payload(self, **overrides):
        data = {
            'nursing_category': 'registered',
            'number_of_nurses': 3,
            'shift_type': 'day',
            'start_date': self.tomorrow,
            'urgency': 'planned',
        }
        data.update(overrides)
        return data

    # ── Create request ───────────────────────────────────────────────────

    def test_create_staffing_request_succeeds(self):
        res = self.client.post('/api/employers/requests/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['nursing_category'], 'registered')
        self.assertEqual(res.data['status'], 'open')

    def test_get_staffing_requests_returns_list(self):
        StaffingRequest.objects.create(
            employer=self.profile,
            nursing_category='enrolled',
            number_of_nurses=2,
            shift_type='night',
            start_date=datetime.date.today() + datetime.timedelta(days=1),
            urgency='urgent',
        )
        res = self.client.get('/api/employers/requests/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    # ── Validation ───────────────────────────────────────────────────────

    def test_zero_nurses_rejected(self):
        res = self.client.post('/api/employers/requests/', self._valid_payload(number_of_nurses=0), format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('number_of_nurses', res.data)

    def test_over_100_nurses_rejected(self):
        res = self.client.post('/api/employers/requests/', self._valid_payload(number_of_nurses=101), format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('number_of_nurses', res.data)

    def test_past_start_date_rejected(self):
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        res = self.client.post('/api/employers/requests/', self._valid_payload(start_date=yesterday), format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_date', res.data)

    def test_end_date_before_start_date_rejected(self):
        res = self.client.post('/api/employers/requests/', self._valid_payload(
            start_date=self.next_week,
            end_date=self.tomorrow,
        ), format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', res.data)

    def test_valid_end_date_after_start_date_accepted(self):
        res = self.client.post('/api/employers/requests/', self._valid_payload(
            start_date=self.tomorrow,
            end_date=self.next_week,
        ), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # ── Permission checks ────────────────────────────────────────────────

    def test_nurse_cannot_submit_staffing_request(self):
        nurse = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Thandi', last_name='Mokoena', role='nurse'
        )
        self.client.force_authenticate(user=nurse)
        res = self.client.post('/api/employers/requests/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_submit_staffing_request(self):
        self.client.force_authenticate(user=None)
        res = self.client.post('/api/employers/requests/', self._valid_payload(), format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
