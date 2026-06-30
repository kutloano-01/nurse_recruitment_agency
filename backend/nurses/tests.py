from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from nurses.models import NurseProfile


class DocumentUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.nurse_user = User.objects.create_user(
            email='nurse@test.com', password='Nurse1234!',
            first_name='Test', last_name='Nurse', role='nurse'
        )
        self.profile = NurseProfile.objects.create(
            user=self.nurse_user,
            id_number='9001015009087',
            phone='0711234567',
            sanc_number='SANC123456',
            nursing_category='registered',
            province='GP',
            city='Johannesburg',
        )
        self.client.force_authenticate(user=self.nurse_user)

    def _make_file(self, name, content=b'test content', content_type='application/pdf'):
        return SimpleUploadedFile(name, content, content_type=content_type)

    # ── Successful uploads ───────────────────────────────────────────────

    def test_pdf_upload_succeeds(self):
        file = self._make_file('cv.pdf')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_jpg_upload_succeeds(self):
        file = self._make_file('id.jpg', content_type='image/jpeg')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'id_document',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_png_upload_succeeds(self):
        file = self._make_file('sanc.png', content_type='image/png')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'sanc_certificate',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_document_associated_with_nurse_profile(self):
        file = self._make_file('cv.pdf')
        self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(self.profile.documents.count(), 1)
        self.assertEqual(self.profile.documents.first().document_type, 'cv')

    # ── Invalid file types ───────────────────────────────────────────────

    def test_exe_file_rejected(self):
        file = self._make_file('malware.exe', content_type='application/octet-stream')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_txt_file_rejected(self):
        file = self._make_file('document.txt', content_type='text/plain')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zip_file_rejected(self):
        file = self._make_file('archive.zip', content_type='application/zip')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── File size limits ─────────────────────────────────────────────────

    def test_file_over_5mb_rejected(self):
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        file = self._make_file('large.pdf', content=large_content)
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_under_5mb_accepted(self):
        small_content = b'x' * (2 * 1024 * 1024)  # 2MB
        file = self._make_file('small.pdf', content=small_content)
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # ── Permission checks ────────────────────────────────────────────────

    def test_unauthenticated_cannot_upload(self):
        self.client.force_authenticate(user=None)
        file = self._make_file('cv.pdf')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_cannot_upload_nurse_document(self):
        employer = User.objects.create_user(
            email='employer@test.com', password='Employer1234!',
            first_name='Test', last_name='Employer', role='employer'
        )
        self.client.force_authenticate(user=employer)
        file = self._make_file('cv.pdf')
        res = self.client.post('/api/nurses/documents/', {
            'document_type': 'cv',
            'file': file
        }, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
