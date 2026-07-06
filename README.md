# NurseConnect — South African Nurse Recruitment Agency

A full-stack web platform for a South African nursing recruitment agency. The platform connects SANC-registered nurses with public and private healthcare facilities across all nine provinces.

---

## Project Overview

NurseConnect is built around two core user journeys:

- **Nurses** looking for temporary, contract, or permanent work
- **Healthcare facilities** looking for qualified, verified nursing staff

The platform is designed to grow from a marketing website into a full business operating platform — handling registrations, document verification, job listings, shift management, and employer requests.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python 3.13, Django 6 |
| Database | SQLite (development) → PostgreSQL (production) |
| API | Django REST Framework |
| File Storage | Django media uploads (local dev) |
| Auth | Session-based with role-based access |
| Hosting (planned) | Afrihost VPS |

---

## Project Structure

```
nurse_recruitment_agency/
├── index.html                  ← Public-facing website
├── frontend/
│   └── login.html              ← Admin login page
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── core/                   ← Django project settings & URLs
│   ├── accounts/               ← Custom user model, auth (register/login/logout)
│   ├── nurses/                 ← Nurse profiles, documents, availability
│   ├── employers/              ← Employer profiles, staffing requests
│   └── jobs/                   ← Job listings, applications
└── venv/                       ← Python virtual environment
```

---

## User Roles

| Role | Permissions |
|---|---|
| Admin | Full access — manage nurses, employers, jobs, documents, users |
| Nurse | Register, upload documents, set availability, apply for jobs |
| Employer | Register facility, submit staffing requests, view bookings |

---

## Database Models

### Accounts
- `User` — custom user model with email login and role field (admin / nurse / employer)

### Nurses
- `NurseProfile` — SANC number, nursing category, speciality, province, verification status
- `NurseDocument` — uploaded files (SANC certificate, ID, CV, qualifications, references, criminal clearance)
- `NurseAvailability` — day and shift availability per nurse

### Employers
- `EmployerProfile` — facility name, type, province, contact details
- `StaffingRequest` — nursing category needed, number of nurses, shift type, urgency, start date

### Jobs
- `Job` — title, facility, province, contract type, salary, description, status
- `JobApplication` — nurse-to-job application with status tracking

---

## API Endpoints

### Accounts
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/accounts/register/` | Register a new user |
| POST | `/api/accounts/login/` | Login |
| POST | `/api/accounts/logout/` | Logout |
| GET | `/api/accounts/me/` | Get current user |

### Nurses
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/nurses/profile/` | Get or create nurse profile |
| PATCH | `/api/nurses/profile/` | Update nurse profile |
| POST | `/api/nurses/documents/` | Upload a document |
| GET / POST | `/api/nurses/availability/` | Get or set availability |
| DELETE | `/api/nurses/availability/<id>/` | Remove an availability slot |

### Employers
| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/employers/profile/` | Get or create employer profile |
| GET / POST | `/api/employers/requests/` | Get or submit staffing requests |

### Jobs
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/jobs/` | List all active jobs (public) |
| GET | `/api/jobs/<id>/` | Get a single job (public) |
| GET / POST | `/api/jobs/applications/` | View or submit job applications |

---

## Frontend Pages

### Public Website (`index.html`)
- Split hero — nurses left, employers right
- Services strip (permanent placement, locum shifts, home care, international)
- Trust bar (SANC verification, flexible placements, nationwide, 24/7 support)
- How We Verify section (6-step screening process)
- Why Choose Us (6 value propositions)
- How It Works (nurse journey + employer journey)
- Job listings
- Home care section
- Footer with nav links and compliance badges

### Nurse Registration Modal (4-step)
- Step 1 — Account (name, email, password)
- Step 2 — Nursing details (SANC number, category, speciality, experience)
- Step 3 — Personal details (ID number, phone, province, city)
- Step 4 — Document uploads (SANC certificate, ID, CV required; qualification optional)

### Employer Registration Modal (4-step)
- Step 1 — Account (name, email, password)
- Step 2 — Facility details (name, type, province, city, address)
- Step 3 — Contact details + POPIA notice
- Step 4 — Staffing needs (category, number of nurses, shift type, urgency, start date)

### Admin Login (`frontend/login.html`)
- Email and password authentication
- Role check — admin accounts only
- Redirects to dashboard on success

---

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd nurse_recruitment_agency
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create an admin user
```bash
python manage.py shell
```
```python
from accounts.models import User
User.objects.create_superuser('admin@nurseconnect.co.za', 'YourPassword123!', first_name='Admin', last_name='User')
```

### 6. Start the backend server
```bash
python manage.py runserver
```

### 7. Serve the frontend
Open a second terminal from the project root:
```bash
python -m http.server 3000
```

Then open:
- **Website** → `http://localhost:3000`
- **Django API** → `http://127.0.0.1:8000`
- **Django Admin** → `http://127.0.0.1:8000/admin`
- **Admin Login** → `http://localhost:3000/frontend/login.html`

---

## MVP Roadmap

- [x] Public website
- [x] Nurse registration modal (4-step, wired to API)
- [x] Employer registration modal (4-step, wired to API)
- [x] Django backend (users, nurses, employers, jobs)
- [x] Database schema
- [x] Admin login page
- [ ] Admin dashboard
- [ ] Dynamic job listings (database-driven)
- [ ] Nurse portal (login, profile, availability)
- [ ] Employer portal (login, requests, bookings)
- [ ] Email notifications (confirmation + admin alerts)
- [ ] PostgreSQL migration for production
- [ ] Deployment to Afrihost VPS

---

## Compliance

- SANC (South African Nursing Council) registration verification
- POPIA (Protection of Personal Information Act) compliant data handling
- CIPC registered business
- APSO member (planned)

---

## Default Admin Credentials (Development Only)

```
Email:    admin@nurseconnect.co.za
Password: Admin1234!
```

> Change these immediately before deploying to production.
