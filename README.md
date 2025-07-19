# Thorpat Django Project

This project is a full-stack application built with Django (backend) and React (frontend), orchestrated with Docker Compose. It features a robust API, user authentication, and a modern dashboard.

## Features

**Backend (Django):**
- RESTful API endpoints for various modules (Users, Activity Log, Cart, Catalogue, Order, Partner, Profiles, Reviews).
- User authentication with JWT (JSON Web Tokens).
- API documentation using `drf-yasg` (Swagger UI/ReDoc).
- PostgreSQL for database management.
- Redis for caching and Celery for asynchronous tasks.

**Frontend (React):**
- Modern and responsive UI built with React and Tailwind CSS.
- User authentication (Login, Register, Forgot Password, Reset Password).
- Dashboard with navigation to user and product management sections.
- Centralized API client for easy interaction with backend services.

## Technologies Used

**Backend:**
- Python 3.x
- Django
- Django REST Framework (DRF)
- `djangorestframework-simplejwt`
- `drf-yasg` (for API documentation)
- PostgreSQL
- Redis
- Celery

**Frontend:**
- React.js
- Vite
- Tailwind CSS
- `react-router-dom`
- `axios`

**Deployment/Orchestration:**
- Docker
- Docker Compose

## Project Structure Overview

```
thorpat-django/
├── backend/                  # Django backend application
│   ├── thorpat/              # Main Django project settings and URLs
│   │   ├── api/              # Centralized API definitions (v1)
│   │   │   ├── v1/           # API Version 1
│   │   │   │   ├── users/    # User API (serializers, views, urls)
│   │   │   │   ├── activitylog/ # ActivityLog API
│   │   │   │   ├── cart/     # Cart API
│   │   │   │   ├── catalogue/ # Catalogue API
│   │   │   │   ├── order/    # Order API
│   │   │   │   ├── partner/  # Partner API
│   │   │   │   ├── profiles/ # Profiles API
│   │   │   │   ├── reviews/  # Reviews API
│   │   │   │   ├── auth/     # Authentication API
│   │   │   │   └── urls.py   # Main API v1 URL dispatcher
│   │   └── apps/             # Django apps (users, cart, catalogue, etc.)
│   └── manage.py
├── frontend/                 # React frontend application
│   ├── shared/               # Shared frontend code (e.g., API clients)
│   │   └── src/api/          # Shared API services (api.js, auth.js, users.js, products.js)
│   └── web/                  # Main web frontend (React components, screens, layouts)
│       ├── src/
│       │   ├── components/
│       │   ├── context/
│       │   ├── layouts/
│       │   └── screens/
│       └── package.json
├── .env                      # Environment variables (local development)
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile.Django         # Dockerfile for Django backend
├── Dockerfile.Base           # Base Dockerfile
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Docker Desktop installed and running.
- Node.js and npm (or yarn) for frontend development.

### 1. Environment Setup

Create a `.env` file in the project root directory (`thorpat-django/`) based on the example below. This file will contain sensitive information and configuration variables.

```dotenv
# .env example
DJANGO_SECRET_KEY='your_django_secret_key_here'
DEBUG=1

POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

MAIL_PASSWORD=your_email_app_password
MAIL_USERNAME=your_email@gmail.com
MAIL_FROM=dev@thorpat.com
MAIL_FROM_NAME="Thorpat Dev"
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=1
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

CLIENT_ID=your_google_client_id
CLIENT_SECRET=your_google_client_secret

# Frontend API Base URL (should match your Django backend URL)
VITE_API_BASE_URL=http://localhost:8000/api
```

**Note:** Replace placeholder values with your actual secret key, email credentials, and Google OAuth client details.

### 2. Build and Run Docker Containers

Navigate to the project root directory in your terminal and run:

```bash
docker-compose up --build -d
```

This command will:
- Build the Docker images for your Django backend and React frontend.
- Start all services defined in `docker-compose.yml` (Django, PostgreSQL, Redis, Celery worker, React development server).
- Run them in detached mode (`-d`).

### 3. Apply Django Migrations

Once the containers are up, apply database migrations for your Django project:

```bash
docker-compose exec django python manage.py migrate
```

### 4. Create a Django Superuser (Optional, but recommended)

To access the Django admin panel and manage data, create a superuser:

```bash
docker-compose exec django python manage.py createsuperuser
```
Follow the prompts to set up your superuser credentials.

### 5. Run Frontend Development Server

The frontend development server is usually started automatically by `docker-compose up`. However, if you need to restart it or run it separately:

Navigate to the frontend web directory:

```bash
cd frontend/web
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

This will typically make the frontend accessible at `http://localhost:5173`.

## Accessing the Application

- **Frontend Application:** `http://localhost:5173`
- **Django Admin Panel:** `http://localhost:8000/admin/`

## API Documentation

Your API documentation is available via `drf-yasg` (Swagger UI and ReDoc):

- **Swagger UI:** `http://localhost:8000/swagger/`
- **ReDoc:** `http://localhost:8000/redoc/`

## Important Notes

- **API Versioning:** The API uses URL path versioning. All API requests should include the version in the path, e.g., `/api/v1/users/`.
- **Authentication:** The API uses JWT for authentication. Obtain tokens via `/api/v1/auth/login/`.
- **Email Configuration:** For password reset and account activation emails to work, ensure your `.env` file has correct `MAIL_` settings for an SMTP server (e.g., Gmail).

---

Feel free to contribute or report issues!
