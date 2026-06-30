from django.core.mail import send_mail
from django.conf import settings


def send_nurse_registration_confirmation(user, profile):
    """Send confirmation email to nurse after registration."""
    send_mail(
        subject='Welcome to NurseConnect — Registration Received',
        message=f"""Hi {user.first_name},

Thank you for registering with NurseConnect.

Your profile has been submitted and is currently under review. Our team will verify your documents and SANC registration within 48 hours.

Your registration details:
- Name: {user.get_full_name()}
- Email: {user.email}
- SANC Number: {profile.sanc_number}
- Nursing Category: {profile.get_nursing_category_display()}
- Province: {profile.get_province_display()}

What happens next?
1. Our team reviews your submitted documents
2. We verify your SANC registration
3. You will receive an email once your profile is approved
4. You will then start receiving suitable shift offers

If you have any questions, please contact us at support@nurseconnect.co.za.

Kind regards,
The NurseConnect Team
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_nurse_registration_admin_notification(user, profile):
    """Notify admin when a new nurse registers."""
    send_mail(
        subject=f'New Nurse Registration — {user.get_full_name()}',
        message=f"""A new nurse has registered on NurseConnect and is awaiting verification.

Nurse Details:
- Name: {user.get_full_name()}
- Email: {user.email}
- SANC Number: {profile.sanc_number}
- Nursing Category: {profile.get_nursing_category_display()}
- Province: {profile.get_province_display()}
- City: {profile.city}
- Years Experience: {profile.years_experience}
- Registered: {profile.created_at.strftime('%d %B %Y at %H:%M')}

Please log in to the admin panel to review and verify this registration.

http://localhost:3000/frontend/login.html
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],
        fail_silently=True,
    )


def send_employer_registration_confirmation(user, profile):
    """Send confirmation email to employer after registration."""
    send_mail(
        subject='Welcome to NurseConnect — Staffing Request Received',
        message=f"""Hi {user.first_name},

Thank you for registering with NurseConnect.

Your facility profile and staffing request have been received. A member of our team will be in touch within 24 hours to discuss your requirements.

Your registration details:
- Contact Name: {user.get_full_name()}
- Email: {user.email}
- Facility: {profile.facility_name}
- Facility Type: {profile.get_facility_type_display()}
- Province: {profile.get_province_display()}

If you have any urgent staffing needs, please contact us directly at placements@nurseconnect.co.za.

Kind regards,
The NurseConnect Team
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_employer_registration_admin_notification(user, profile):
    """Notify admin when a new employer registers."""
    send_mail(
        subject=f'New Employer Registration — {profile.facility_name}',
        message=f"""A new employer has registered on NurseConnect.

Employer Details:
- Facility: {profile.facility_name}
- Facility Type: {profile.get_facility_type_display()}
- Province: {profile.get_province_display()}
- City: {profile.city}
- Contact Person: {profile.contact_person}
- Email: {user.email}
- Phone: {profile.phone}
- Registered: {profile.created_at.strftime('%d %B %Y at %H:%M')}

Please log in to the admin panel to review this registration.

http://localhost:3000/frontend/login.html
""",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.DEFAULT_FROM_EMAIL],
        fail_silently=True,
    )
