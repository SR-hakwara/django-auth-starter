# 🔐 django-auth-basic

A modern, production-ready Django authentication starter kit. Free, open source, and multilingual.

![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Django 6+](https://img.shields.io/badge/Django-6+-092E20?logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-CDN-06B6D4?logo=tailwindcss&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/tests-40%20passed-brightgreen)

---

## ✨ Features

- **Email or username authentication** — login with either
- **Custom User Model** — `AbstractBaseUser` + `PermissionsMixin`
- **Email verification** — token-based email activation (expires in 24h)
- **Password reset** — secure reset flow via email
- **User profile** — view & edit profile, avatar upload with server-side validation
- **Login rate limiting** — atomic, IP-based brute-force protection (Redis in production)
- **Open redirect protection** — `?next=` parameter validated before redirect
- **CSRF-safe logout** — logout only via POST
- **i18n ready** — built-in translation support (EN/FR)
- **Premium UI** — TailwindCSS + HTMX + Alpine.js
- **Clean Architecture** — views → services → selectors
- **Security hardened** — CSRF, HSTS, secure cookies, non-root Docker user

---

## 🏗️ Architecture

```
auth_starter_basic/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── dev.py           # Development (SQLite, Mailpit)
│   │   └── prod.py          # Production (PostgreSQL, Redis, SMTP, HSTS)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/             # Utilities, validators, constants (INPUT_CSS, avatar validator)
│   ├── users/            # CustomUser model and admin
│   ├── authentication/   # Login, registration, password reset, activation flows
│   ├── profiles/         # User profile views, forms, avatar updates, password change
│   └── emails/           # Email dispatch services
├── templates/
│   ├── base.html         # Base layout
│   ├── authentication/   # Auth pages
│   ├── profiles/         # Profile pages
│   └── emails/           # Email templates
├── locale/               # Translation files (EN/FR)
├── static/css/styles.css
├── tests/                # Full test suite (40 tests)
├── manage.py
├── requirements.txt
├── Makefile
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/django-auth-basic.git
cd django-auth-basic

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env — DJANGO_SECRET_KEY is required
```

> Generate a secret key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 3. Migrate & Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 4. Visit

- **Login:** http://127.0.0.1:8000/auth/login/
- **Register:** http://127.0.0.1:8000/auth/register/
- **Admin:** http://127.0.0.1:8000/admin/

> **Dev mode:** Activation emails are sent via Mailpit. Start it with `docker compose up mailpit` and visit http://localhost:8025.

---

## 🐳 Docker Compose (Recommended)

The included `docker-compose.yml` starts the full stack: PostgreSQL, Redis, and Mailpit.

```bash
# Start all services in development mode
docker compose up

# Apply migrations
docker compose exec web python manage.py migrate

# Create a superuser
docker compose exec web python manage.py createsuperuser
```

| Service | URL |
|---|---|
| Django app | http://localhost:8000 |
| Mailpit (email UI) | http://localhost:8025 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## 🔧 Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | **Yes** | — | Django secret key — generate one, never reuse |
| `DJANGO_DEBUG` | No | `False` | Enable debug mode |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hosts |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `REDIS_URL` | Prod | `redis://redis:6379/1` | Redis URL for shared cache |
| `EMAIL_BACKEND` | No | Console | Email backend class |
| `DEFAULT_FROM_EMAIL` | No | `noreply@example.com` | Sender email address |
| `SECURE_SSL_REDIRECT` | No | `True` (prod) | Redirect HTTP to HTTPS |

---

## 🔒 Security

### Built-in Protections

| Feature | Implementation |
|---|---|
| CSRF | Django middleware + POST-only logout |
| Open Redirect | `url_has_allowed_host_and_scheme` on `?next=` |
| XSS | `SECURE_CONTENT_TYPE_NOSNIFF = True` |
| Clickjacking | `X_FRAME_OPTIONS = "DENY"` |
| Password Hashing | PBKDF2 (Django default) |
| Rate Limiting | Atomic IP-based, 5 attempts / 5 min (Redis in prod) |
| Token Expiry | Email & password-reset tokens expire in 24h (`PASSWORD_RESET_TIMEOUT`) |
| Avatar Upload | Server-side: max 2 MB, magic-byte MIME check (JPEG/PNG/WebP only) |
| Docker | Non-root `appuser` in container |

### Production Settings (`prod.py`)

- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_SSL_REDIRECT = True`
- `HSTS` enabled (1 year, preload, subdomains)
- `CACHES` → Redis (shared cache across all Gunicorn workers)
- `CONN_MAX_AGE = 60` (PostgreSQL connection pooling)

---

## 🌍 Internationalization

The project is i18n ready with `LocaleMiddleware` and a `locale/` directory pre-created.

```python
# config/settings/base.py
LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]
```

Generate translation files:

```bash
python manage.py makemessages -l fr
python manage.py compilemessages
```

---

## 🧪 Testing

```bash
# Run all 40 tests
pytest -v

# With coverage report
pytest --cov=apps --cov-report=term-missing
```

### Test Coverage

| Module | Cases covered |
|---|---|
| `authentication` | Login (email + username), logout POST/GET, rate limiting, open redirect, register, activation, password reset confirm |
| `profiles` | Profile view, update, email change triggers re-verification, password change |
| `users` | Model creation, superuser, email normalization, `__str__` |

---

## 🐳 Docker (Production Build)

```bash
# Build the image (pass a build-time key for collectstatic)
docker build --build-arg SECRET_KEY_BUILD=any-temp-key -t django-auth-basic .

# Run with a real .env in production
docker run -p 8000:8000 --env-file .env django-auth-basic
```

The container runs as a non-root user (`appuser`) for improved security.

---

## 📝 Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make migrate` | Run migrations |
| `make run` | Start dev server |
| `make test` | Run tests |
| `make lint` | Lint with ruff |
| `make format` | Format with black |
| `make check` | Django deploy checks |

---

## 🛠️ Tech Stack

- **Python** 3.12+ / **Django** 6+
- **TailwindCSS** (CDN) + **HTMX** + **Alpine.js**
- **PostgreSQL** (prod) / **SQLite** (dev)
- **Redis** (prod, rate limiting cache)
- **WhiteNoise** for static files
- **Gunicorn** WSGI server
- **django-environ** for configuration
- **pytest** + **pytest-django** for testing

---

## 📋 Changelog

### v1.1.0 — Security & Quality Audit (2026-03-11)

Full audit performed — see [AUDIT.md](AUDIT.md) for details.

**Security fixes:**
- Logout converted to POST-only (CSRF logout attack prevention)
- Open redirect via `?next=` blocked with `url_has_allowed_host_and_scheme`
- Rate limiting made atomic (`cache.add` + `cache.incr`) to prevent race conditions
- Rate limiting applied to password reset and resend-activation endpoints
- Avatar uploads validated server-side (2 MB max, magic-byte MIME check)
- `DJANGO_SECRET_KEY` is now required — no insecure default
- Redis cache configured in production for shared rate limiting across workers
- `gunicorn` and `django-redis` added to `requirements.txt`

**Bug fixes:**
- Admin `add_fieldsets` now includes password fields
- Duplicate database indexes removed from `CustomUser`
- `PASSWORD_RESET_TIMEOUT = 86400` replaces the unused `EMAIL_TOKEN_EXPIRY_HOURS`
- Dockerfile runs as non-root user; `collectstatic` errors are no longer silenced

**Quality improvements:**
- `INPUT_CSS` centralized in `apps/core/constants.py`
- Cross-app import (`profiles` → `authentication`) removed
- `SECURE_BROWSER_XSS_FILTER` (removed in Django 4.0) cleaned up
- Security logging configured for authentication events
- `CONN_MAX_AGE = 60` for PostgreSQL connection pooling in production
- `locale/` directory created for i18n support
- `.env.example` updated with all variables including `REDIS_URL`
- `docker-compose.yml` added (PostgreSQL + Redis + Mailpit)
- Test suite expanded from 8 to 40 tests with full coverage

---

## 📄 License

MIT — free for personal and commercial use.


---

## ✨ Features

- **Email-based authentication** — no usernames, just email + password
- **Custom User Model** — `AbstractBaseUser` + `PermissionsMixin`
- **Email verification** — token-based email activation
- **Password reset** — secure reset flow via email
- **User profile** — view & edit profile
- **Login rate limiting** — IP-based brute-force protection
- **i18n ready** — built-in translation support (EN/FR)
- **Premium UI** — TailwindCSS + HTMX + Alpine.js
- **Clean Architecture** — views → services → selectors
- **Security hardened** — CSRF, XSS, HSTS, secure cookies

---

## 🏗️ Architecture

```
auth_starter_basic/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── dev.py           # Development (SQLite, console email)
│   │   └── prod.py          # Production (PostgreSQL, SMTP, HSTS)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── core/             # Base utilities, validators, constants
│   ├── users/            # CustomUser model and admin
│   ├── authentication/   # Login, registration, password reset flows
│   ├── profiles/         # User profile views, forms, avatar updates
│   └── emails/           # Email dispatch services
├── templates/
│   ├── base.html         # Base layout
│   ├── authentication/   # Auth pages
│   ├── profiles/         # Profile pages
│   └── emails/           # Email templates
├── static/css/styles.css
├── manage.py
├── requirements.txt
├── Makefile
├── Dockerfile
└── pyproject.toml
```

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/django-auth-basic.git
cd django-auth-basic

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY is required)
```

### 3. Migrate & Run

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 4. Visit

- **Login:** http://127.0.0.1:8000/auth/login/
- **Register:** http://127.0.0.1:8000/auth/register/
- **Admin:** http://127.0.0.1:8000/admin/

> **Dev mode:** Activation emails are printed to the console. Copy the link from the terminal to activate accounts.

---

## 🔧 Configuration

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | **Required.** Django secret key |
| `DJANGO_DEBUG` | `False` | Enable debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
| `DATABASE_URL` | SQLite | Database connection string |
| `EMAIL_BACKEND` | Console | Email backend class |
| `DEFAULT_FROM_EMAIL` | `noreply@example.com` | Sender email address |

---

## 🔒 Security

### Built-in Protections

| Feature | Implementation |
|---|---|
| CSRF | Django middleware (default) |
| XSS | `SECURE_BROWSER_XSS_FILTER = True` |
| Content Sniffing | `SECURE_CONTENT_TYPE_NOSNIFF = True` |
| Clickjacking | `X_FRAME_OPTIONS = "DENY"` |
| Password Hashing | PBKDF2 (Django default) |
| Rate Limiting | IP-based, 5 attempts / 5 min |
| Token Expiry | Email tokens expire in 24h |

### Production Settings (`prod.py`)

- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_SSL_REDIRECT = True`
- `HSTS` enabled (1 year, preload)

---

## 🌍 Internationalization

The project is i18n ready:

```python
# config/settings/base.py
LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]
```

All strings use `gettext_lazy`. Generate translation files:

```bash
python manage.py makemessages -l fr
python manage.py compilemessages
```

---

## 🧪 Testing

```bash
# Run all tests
pytest -v

# With coverage
pytest --cov=apps
```

---

## 🐳 Docker

```bash
docker build -t django-auth-basic .
docker run -p 8000:8000 --env-file .env django-auth-basic
```

---

## 📝 Makefile Commands

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make migrate` | Run migrations |
| `make run` | Start dev server |
| `make test` | Run tests |
| `make lint` | Lint with ruff |
| `make format` | Format with black |
| `make check` | Django deploy checks |

---

## 🛠️ Tech Stack

- **Python** 3.12+ / **Django** 5+
- **TailwindCSS** (CDN) + **HTMX** + **Alpine.js**
- **PostgreSQL** (prod) / **SQLite** (dev)
- **WhiteNoise** for static files
- **django-environ** for configuration
- **pytest** + **pytest-django** for testing

---

## 📄 License

MIT — free for personal and commercial use.
