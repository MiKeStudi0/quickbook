# QuickBook — Event Booking & Binary Referral Platform

QuickBook is an event booking backend platform built with **Python**, **Django 5**, and **Django REST Framework (DRF)**. The platform provides REST APIs for high-concurrency ticket reservations using database row locking, an automated multi-level binary referral network powered by Breadth-First Search (BFS) placement, and a custom Staff & Vendor Management Dashboard.

---

## Quick Access

### Production URLs
- **Live Application**: [http://quickbook.midhunnk.in](http://quickbook.midhunnk.in)
- **Swagger UI**: [http://quickbook.midhunnk.in/api/docs/](http://quickbook.midhunnk.in/api/docs/)
- **OpenAPI Schema**: [http://quickbook.midhunnk.in/api/schema/](http://quickbook.midhunnk.in/api/schema/)
- **ReDoc API Documentation**: [http://quickbook.midhunnk.in/api/redoc/](http://quickbook.midhunnk.in/api/redoc/)
- **Staff & Vendor Dashboard**: [http://quickbook.midhunnk.in/dashboard/](http://quickbook.midhunnk.in/dashboard/)
- **Customer Web Portal**: [http://quickbook.midhunnk.in/customer/login/](http://quickbook.midhunnk.in/customer/login/)

### Local Development URLs
- **Local Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Local Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Local OpenAPI Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- **Local ReDoc**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **Local Staff Dashboard**: [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)

### GitHub Repository
- **Repository URL**: [https://github.com/MiKeStudi0/quickbook](https://github.com/MiKeStudi0/quickbook)

---

## Tech Stack

| Component | Technology | Usage in Repository |
|---|---|---|
| **Language** | Python 3.11+ | Core runtime language |
| **Web Framework** | Django 5.2+ | Core application framework & ORM |
| **REST Framework** | Django REST Framework | RESTful API views, serializers & pagination |
| **Authentication** | SimpleJWT | JWT access and refresh token authentication |
| **Filtering** | `django-filter` | Backend search, date, and vendor filtering |
| **API Schema** | `drf-spectacular` | OpenAPI 3.0 schema generation, Swagger UI & ReDoc |
| **Database** | SQLite 3 | Embedded database (`db.sqlite3`) as required |
| **WSGI Server** | Gunicorn | Production application server (listening on `127.0.0.1:8001`) |
| **Reverse Proxy** | Nginx | Production web server handling HTTP requests |

---

## Machine Test Requirements Compliance

| Requirement | Status | Implementation Details |
|---|---|---|
| **User Registration** | ✅ Implemented | `POST /api/auth/register/` (Auto-generates unique 8-character referral code) |
| **User Login** | ✅ Implemented | `POST /api/auth/login/` (Returns JWT access & refresh tokens) |
| **User Logout** | ✅ Implemented | `POST /api/auth/logout/` (Blacklists refresh token) |
| **Token Authentication** | ✅ Implemented | SimpleJWT Bearer authentication on protected routes |
| **Protected APIs** | ✅ Implemented | `IsAuthenticated` permission guards across bookings & user endpoints |
| **Event Browsing** | ✅ Implemented | `GET /api/events/` and `GET /api/events/<id>/` |
| **Event Search/Filtering** | ✅ Implemented | Backend query filtering by keyword (`search`), `vendor`, and `date` |
| **Ticket Booking** | ✅ Implemented | `POST /api/events/<pk>/book/` with seat availability checks |
| **Booking Cancellation** | ✅ Implemented | `POST /api/bookings/<pk>/cancel/` (restores seat availability) |
| **Booking History** | ✅ Implemented | `GET /api/bookings/` filtered by user role and status |
| **Seat Availability** | ✅ Implemented | Validated under lock prior to updating seat counts |
| **Concurrent Booking Protection** | ✅ Implemented | `transaction.atomic()` with `select_for_update()` database row locking |
| **Binary Referral System** | ✅ Implemented | Auto-generated referral codes and linked user node placement |
| **Automatic Node Placement** | ✅ Implemented | Breadth-First Search (BFS) level-order tree placement in `referrals/services.py` |
| **Referral Tree API** | ✅ Implemented | `GET /api/referrals/<user_id>/tree/` (Returns full nested JSON tree) |
| **Referral Root API** | ✅ Implemented | `GET /api/referrals/<user_id>/root/` (Ascends tree to top ancestor) |
| **Referral Statistics API** | ✅ Implemented | `GET /api/referrals/<user_id>/stats/` (`left_count`, `right_count`, `total_network`) |
| **Custom Staff Dashboard** | ✅ Implemented | Dedicated dashboard at `/dashboard/` (no Django admin dependency) |
| **Vendor Management** | ✅ Implemented | View, create, and update vendor accounts (`/dashboard/vendors/`) |
| **Event Management** | ✅ Implemented | View, create, update, search, and filter events (`/dashboard/events/`) |
| **User Management** | ✅ Implemented | View users list, user details, and interactive referral tree search (`/dashboard/users/`) |
| **Swagger/OpenAPI Docs** | ✅ Implemented | Mounted at `/api/docs/` and `/api/schema/` |
| **Rate Limiting** | ✅ Implemented | DRF Throttling (`AnonRateThrottle` 100/day, `UserRateThrottle` 1000/day) |

---

## API Endpoints Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user with optional referral code | No |
| `POST` | `/api/auth/login/` | Login and receive JWT access & refresh tokens | No |
| `POST` | `/api/auth/logout/` | Blacklist refresh token and logout | Yes |
| `GET` | `/api/auth/me/` | Retrieve authenticated user profile details | Yes |

### Events

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/events/` | Browse events with search, date, vendor filter & pagination | No |
| `POST` | `/api/events/` | Create a new event (Staff or Vendor) | Yes |
| `GET` | `/api/events/<id>/` | Retrieve details for a specific event | No |
| `PUT` / `PATCH` | `/api/events/<id>/` | Update an existing event | Yes |
| `DELETE` | `/api/events/<id>/` | Delete an event | Yes |
| `POST` | `/api/events/<pk>/book/` | Book tickets for an event (atomic row locked) | Yes |

### Bookings

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/bookings/` | Retrieve user booking history (Staff views all) | Yes |
| `POST` | `/api/bookings/<pk>/cancel/` | Cancel booking and restore available seats | Yes |

### Referrals

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/referrals/<user_id>/tree/` | Retrieve full binary referral tree JSON structure | No |
| `GET` | `/api/referrals/<user_id>/root/` | Find top root ancestor node for user | No |
| `GET` | `/api/referrals/<user_id>/stats/` | Retrieve left team count, right team count & total network | No |

---

## Architecture & Request Flow

### Application Structure

```text
quickbook/
├── accounts/          # Custom User model, auth views, JWT serializers & signals
├── events/            # Event model, views, filters, and serializers
├── bookings/          # Booking model, atomic reservation logic & cancellation
├── referrals/         # ReferralNode model, BFS placement service & tree serializers
├── dashboard/         # Custom Staff & Vendor management views and templates
├── config/            # Django settings, URL routing, and OpenAPI configuration
├── manage.py          # Django management script
├── requirements.txt   # Project dependencies
└── README.md          # Project documentation
```

### Request Flow
```text
HTTP Client (REST / Web)
   └── Django URL Router (config/urls.py)
        └── API View / Class-Based View
             ├── DRF Serializer (Validation & Deserialization)
             ├── Service Layer (referrals/services.py & Atomic Transactions)
             └── Django ORM (Database query with select_for_update)
```

---

## Booking Consistency & Concurrency Protection

To ensure high concurrency safety and prevent double-booking under simultaneous traffic:

- Ticket reservation in `BookEventView` (`bookings/views.py`) executes inside `transaction.atomic()`.
- The target event record is fetched using `Event.objects.select_for_update()`, acquiring an exclusive row-level database lock.
- Available seat validation is performed under lock (`available_seats >= quantity`).
- Upon verification, seat counts are decremented atomically and saved before releasing the lock.
- Operational retry logic is implemented to handle lock contention cleanly.

---

## Binary Referral Network System

- **Referral Code Generation**: When a user registers, an 8-character uppercase hex code is automatically generated (`accounts/models.py`).
- **Placement Algorithm**: When a user registers with a valid referral code:
  1. The referrer's node is located in the `ReferralNode` table.
  2. Level-Order Breadth-First Search (BFS) in `referrals/services.py` traverses the tree to find the first open `left` or `right` child position.
  3. The new user's node is linked to the parent at the open slot.
- **Tree & Metrics**: The API calculates left branch count, right branch count, total network size, and returns nested tree objects or top root nodes.

---

## Setup & Local Development

### 1. Clone & Navigate
```bash
git clone https://github.com/MiKeStudi0/quickbook.git
cd quickbook
```

### 2. Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Seed Data
```bash
# Run database migrations
python manage.py migrate

# Seed demo users, realistic events, bookings & binary referral tree
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver
```

---

## Seeded Demo Credentials

| Role | Username | Password | Notes |
|---|---|---|---|
| **Staff Admin** | `admin` | `admin123` | Full access to `/dashboard/` |
| **Vendor** | `nexus_events` | `vendor123` | Nexus Events Corp vendor portal |
| **Customer (Tree Root)** | `alex_morgan` | `customer123` | Root of binary referral tree (`5C22E205`) |
| **Customer (Left Child)** | `sarah_connor` | `customer123` | Placed at `alex_morgan.left` |
| **Customer (Right Child)**| `david_miller` | `customer123` | Placed at `alex_morgan.right` |

---

## Automated Test Suite

The repository includes 29 unit tests covering authentication, atomic booking concurrency, referral tree placement, and dashboard views.

Run the test suite:
```bash
python manage.py test
```

---

## Production Deployment Architecture

```text
Internet Client
   └── Nginx (Port 80)
        └── Gunicorn WSGI (127.0.0.1:8001)
             └── Django 5 Application
                  └── SQLite Database (db.sqlite3)
```

- **Live URL**: [http://quickbook.midhunnk.in](http://quickbook.midhunnk.in)
- **Gunicorn Internal Socket**: `127.0.0.1:8001`
- **Static Assets**: Served via Nginx at `/static/`
