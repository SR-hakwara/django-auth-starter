# 🔐 django-auth-basic

A modern, production-ready Django authentication starter kit. Free, open source, and multilingual.

![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Django 5+](https://img.shields.io/badge/Django-5+-092E20?logo=django&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-CDN-06B6D4?logo=tailwindcss&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

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
